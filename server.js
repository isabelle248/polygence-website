// Import modules 
//(web framework, middleware for handling file uploads, work w/ file paths)
const express = require('express');
const multer = require('multer');
const path = require('path');
const { spawn } = require('child_process');

// creates Express app (web server, listen on port 3000)
const app = express();
const port = 3000;

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
const upload = multer({ storage: storage });

// Serve static files from the 'public' folder
app.use(express.static('public'));

// Route to handle file uploads
app.post('/upload', upload.single('myFile'), (req, res) => {
    const tempo = req.body.tempo;

    if (!req.file) { // if file not uploaded
       return res.status(400).send('No file uploaded.');
    }

    // joins folder and filename into complete file path
    const pdfPath = path.join(__dirname, 'uploads', req.file.filename);
    // path to shell script
    const audiverisScript = path.join(__dirname, 'scripts', 'polygence.sh');

    // set headers for live streaming
    res.setHeader('Content-Type', 'text/plain'); // tells browser is plain text
    res.setHeader('Transfer-Encoding', 'chunked'); // stream data in chunks

    // confirm what file/tempo user inputted
    res.write(`File uploaded: ${req.file.filename}\nTempo: ${tempo}\n\n`);

    // Run Audiveris
    // run shell script with arguments ($1 = pdf file path)
    const audiverisProcess = spawn('bash', [audiverisScript, pdfPath])

    let mxlFilePath = '';

    // stream standard output of shell script to browser
    audiverisProcess.stdout.on('data', (data) => {
        const text = data.toString();
        res.write(text);

        // Capture last line containing .mxl file path
        const match = text.match(/Generated MXL: (.+\.mxl)/);
        if (match) {
            mxlFilePath = match[1].trim();
        }
    })

    // stream error messages from script to browser
    audiverisProcess.stderr.on('data', (data) => {
        res.write(`ERROR: ${data.toString()}`);
    });

    // close response when script finishes
    audiverisProcess.on('close', (code) => {
        res.write(`\nProcess exited with code ${code}\n`);

        if (!mxlFilePath) {
            res.write('No file detected, stopping. \n');
            return res.end();
        }

        res.write('\n--- Python CREPE Output ---\n');
        
        // Run python
        const pythonProcess = spawn('python3', ['/Users/isabellelin/Documents/polygence_code/scripts/run_crepe.py', mxlFilePath, tempo]);

        pythonProcess.stdout.on('data', (data) => res.write(data.toString()));
        pythonProcess.stderr.on('data', (data) => res.write(`Python ERROR: ${data.toString()}`));
        pythonProcess.on('close', (pCode) => {
            res.write(`\nPython script exited with code ${pCode}\n`);
            res.end();
        })
    });


});

// Start the server
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
