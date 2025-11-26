const express = require('express');
const cors = require('cors');
const db = require('./models/database');
const productRoutes = require('./routes/products');
const cartRoutes = require('./routes/cart');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

app.use('/api/products', productRoutes);
app.use('/api/cart', cartRoutes);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
