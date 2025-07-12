const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3002;

app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Ensure uploads directory exists
if (!fs.existsSync(path.join(__dirname, 'uploads'))) {
  fs.mkdirSync(path.join(__dirname, 'uploads'));
}

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, 'uploads'));
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage });

// --- Media Upload Endpoints ---
app.post('/api/upload', upload.single('media'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  res.json({ url: `/uploads/${req.file.filename}` });
});

app.get('/api/media', (req, res) => {
  fs.readdir(path.join(__dirname, 'uploads'), (err, files) => {
    if (err) return res.status(500).json({ error: 'Failed to list files' });
    res.json(files.map(f => ({ url: `/uploads/${f}` })));
  });
});

app.delete('/api/media/:filename', (req, res) => {
  const filePath = path.join(__dirname, 'uploads', req.params.filename);
  fs.unlink(filePath, err => {
    if (err) return res.status(404).json({ error: 'File not found' });
    res.json({ success: true });
  });
});

// --- Reviews Endpoints ---
const REVIEWS_FILE = path.join(__dirname, 'reviews.json');

function readReviews() {
  if (!fs.existsSync(REVIEWS_FILE)) return [];
  return JSON.parse(fs.readFileSync(REVIEWS_FILE, 'utf8'));
}
function writeReviews(reviews) {
  fs.writeFileSync(REVIEWS_FILE, JSON.stringify(reviews, null, 2));
}

app.get('/api/reviews', (req, res) => {
  res.json(readReviews());
});

app.post('/api/reviews', (req, res) => {
  const { name, review, rating } = req.body;
  if (!name || !review || !rating) return res.status(400).json({ error: 'Missing fields' });
  const reviews = readReviews();
  reviews.unshift({ name, review, rating, date: new Date().toISOString() });
  writeReviews(reviews);
  res.json({ success: true });
});

app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
}); 