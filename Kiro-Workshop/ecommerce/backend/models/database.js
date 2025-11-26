const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbDir = path.join(__dirname, '../database');
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

const db = new sqlite3.Database(path.join(dbDir, 'ecommerce.db'));

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    emoji TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    category TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
  )`);

  db.get('SELECT COUNT(*) as count FROM products', (err, row) => {
    if (row.count === 0) {
      const products = [
        ['Laptop Pro', '💻', 1299.99, 'High-performance laptop', 'Electronics'],
        ['Smartphone X', '📱', 899.99, 'Latest smartphone', 'Electronics'],
        ['Wireless Headphones', '🎧', 199.99, 'Noise-canceling headphones', 'Audio'],
        ['Smart Watch', '⌚', 349.99, 'Fitness tracking watch', 'Wearables'],
        ['Camera DSLR', '📷', 1499.99, 'Professional camera', 'Photography'],
        ['Gaming Console', '🎮', 499.99, 'Next-gen gaming', 'Gaming'],
        ['Tablet Plus', '📱', 599.99, 'Portable tablet', 'Electronics'],
        ['Bluetooth Speaker', '🔊', 79.99, 'Portable speaker', 'Audio'],
        ['Keyboard Mechanical', '⌨️', 149.99, 'RGB mechanical keyboard', 'Accessories'],
        ['Mouse Wireless', '🖱️', 49.99, 'Ergonomic mouse', 'Accessories'],
        ['Monitor 4K', '🖥️', 699.99, '27-inch 4K display', 'Electronics'],
        ['Webcam HD', '📹', 89.99, '1080p webcam', 'Accessories'],
        ['External SSD', '💾', 179.99, '1TB storage', 'Storage'],
        ['Power Bank', '🔋', 39.99, '20000mAh capacity', 'Accessories'],
        ['USB Hub', '🔌', 29.99, '7-port USB hub', 'Accessories'],
        ['Desk Lamp', '💡', 44.99, 'LED desk lamp', 'Office'],
        ['Office Chair', '🪑', 299.99, 'Ergonomic chair', 'Furniture'],
        ['Backpack Tech', '🎒', 79.99, 'Laptop backpack', 'Accessories'],
        ['Water Bottle', '💧', 24.99, 'Insulated bottle', 'Lifestyle'],
        ['Coffee Maker', '☕', 129.99, 'Programmable coffee maker', 'Kitchen']
      ];

      const stmt = db.prepare('INSERT INTO products (name, emoji, price, description, category) VALUES (?, ?, ?, ?, ?)');
      products.forEach(p => stmt.run(p));
      stmt.finalize();
    }
  });
});

module.exports = db;
