const express = require('express');
const router = express.Router();
const db = require('../models/database');

router.get('/', (req, res) => {
  db.all(`
    SELECT c.id, c.quantity, p.* 
    FROM cart c 
    JOIN products p ON c.product_id = p.id
  `, (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

router.post('/', (req, res) => {
  const { product_id, quantity } = req.body;
  db.get('SELECT * FROM cart WHERE product_id = ?', [product_id], (err, row) => {
    if (row) {
      db.run('UPDATE cart SET quantity = quantity + ? WHERE product_id = ?', [quantity, product_id], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ id: row.id, message: 'Cart updated' });
      });
    } else {
      db.run('INSERT INTO cart (product_id, quantity) VALUES (?, ?)', [product_id, quantity], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ id: this.lastID, message: 'Added to cart' });
      });
    }
  });
});

router.put('/:id', (req, res) => {
  const { quantity } = req.body;
  db.run('UPDATE cart SET quantity = ? WHERE id = ?', [quantity, req.params.id], function(err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: 'Quantity updated' });
  });
});

router.delete('/:id', (req, res) => {
  db.run('DELETE FROM cart WHERE id = ?', [req.params.id], function(err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: 'Item removed' });
  });
});

module.exports = router;
