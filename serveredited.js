// Import modules 
//(web framework, middleware for handling file uploads, work w/ file paths)
const express = require('express');
const multer = require('multer');
const path = require('path');
const { spawn } = require('child_process');

// creates Express app (web server, listen on port 3000)
const app = express();
const port = 3000;

// EJS setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// middleware to parse text fields from forms
app.use(express.urlencoded({ extended: true }));

// Configure Multer for disk storage
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/'); // Files stored in the 'uploads/' folder
    },
    filename: function (req, file, cb) {
        // Generate new filename using timestamp and original extension
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

// Create the Multer upload middleware
const upload = multer({ storage: storage }).fields([
    { name: 'pdfFile', maxCount: 1 },
    { name: 'audioFile', maxCount: 1 }
])

// Serve static files from the 'public' folder
app.use(express.static('public'));

function runAudiveris(pdfPath) {
    return new Promise((resolve, reject) => {
        const audiverisScript = path.join(__dirname, 'scripts', 'polygence.sh');
        const audiverisProcess = spawn('bash', [audiverisScript, pdfPath]);

        let outputData = '';

        audiverisProcess.stdout.on('data', (data) => {
            outputData += data.toString();
        });

        audiverisProcess.stderr.on('data', (data) => {
            console.error('Audiveris STDERR:', data.toString());
        });

        audiverisProcess.on('close', (code) => {
            // Look for the generated MXL file path in stdout
            const match = outputData.match(/Generated MXL:\s*(.*)/);
            if (match) {
                let filePath = match[1].trim();
                if (!path.isAbsolute(filePath)) {
                    filePath = path.join(__dirname, filePath);
                }
                resolve(filePath);
            } else {
                reject(new Error('No MXL file detected'));
            }
        });
    });
}

function runPythonScript(scriptPath, args = []) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python3', [scriptPath, ...args]);

        let outputData = '';
        let errorData = '';

        // Capture Python stdout (your feedback JSON)
        pythonProcess.stdout.on('data', (data) => {
            outputData += data.toString();
        });

        // Capture Python stderr (optional, for debugging)
        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
            console.error('Python STDERR:', data.toString());
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                return reject(new Error(`Python exited with code ${code}\n${errorData}`));
            }

            try {
                // Expect Python to output JSON string
                const feedbackJSON = JSON.parse(outputData);
                resolve(feedbackJSON);
            } catch (err) {
                reject(new Error('Failed to parse Python JSON output: ' + err.message));
            }
        });
    });
}

// Route to handle file uploads
app.post('/upload', upload, async (req, res) => {
    try {
        // Check if both files were uploaded
        if (!req.files || !req.files.pdfFile || !req.files.audioFile) {
            return res.status(400).send('PDF and audio files are required.');
        }

        const pdfPath = path.join(__dirname, 'uploads', req.files.pdfFile[0].filename);
        const audioPath = path.join(__dirname, 'uploads', req.files.audioFile[0].filename);
        const tempo = req.body.tempo;

        // Run Audiveris to convert PDF → MXL
        const mxlFilePath = await runAudiveris(pdfPath);

        if (!mxlFilePath) {
            return res.status(500).send('No MXL file detected.');
        }

        // Run Python CREPE script to get feedback JSON
        const pythonScript = path.join(__dirname, 'scripts', 'run_crepe.py');
        const feedbackJSON = await runPythonScript(pythonScript, [mxlFilePath, audioPath, tempo]);

        // Render feedback page using EJS
        res.render('feedback', { results: feedbackJSON });

    } catch (err) {
        console.error(err);
        res.status(500).send("Error processing files.");
    }
});


// Start the server
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
