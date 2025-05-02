const express = require('express');
const mongoose = require('mongoose');
const app = express();

mongoose.connect('mongodb://localhost:27017/ai_results', { useNewUrlParser: true });

const ImageSchema = new mongoose.Schema({
    filename: String,
    image: String
});

const Image = mongoose.model('Image', ImageSchema, 'results');

app.get('/get-image/:filename', async (req, res) => {
    const result = await Image.findOne({ filename: req.params.filename });
    if (!result) return res.status(404).send('Image not found');

    const img = Buffer.from(result.image, 'base64');
    res.writeHead(200, {
        'Content-Type': 'image/jpeg',
        'Content-Length': img.length
    });
    res.end(img);
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));
