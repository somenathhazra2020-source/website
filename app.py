import streamlit as st, sqlite3, hashlib, hmac, os, random, base64, re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote
from functools import lru_cache
from pathlib import Path

DB='bharatmart_final.db'
START=1_000_000_000.0
STEPS=['ORDER PLACED','CAME TO STORE','PACKED','OUT FOR DELIVERY','DELIVERED']
IST=ZoneInfo('Asia/Kolkata')
CATS=['Grocery','Vegetables','Fruits','Electronics','Fashion','Kids & Baby','Dairy','Meat & Fish','Beauty & Personal Care','Home & Kitchen','Books & Stationery','Sports & Fitness','Mobile Accessories','Pet Supplies','Automobile','Jewellery','Medicine & Health','Festival & Decoration','Gaming Zone','Smart AI Devices']
BASE={'Grocery': ['Basmati Rice 5kg', 'Brown Rice 1kg', 'Sona Masoori Rice 5kg', 'Wheat Flour 5kg', 'Multigrain Atta 5kg', 'Maida 1kg', 'Sugar 1kg', 'Iodised Salt 1kg', 'Mustard Oil 1L', 'Sunflower Oil 1L', 'Olive Oil 500ml', 'Assam Tea 250g', 'Instant Coffee 100g', 'Marie Biscuits 800g', 'Chocolate Cookies 300g', 'Masala Noodles 560g', 'Penne Pasta 500g', 'Rolled Oats 1kg', 'Forest Honey 500g', 'Mixed Fruit Jam 500g', 'Tomato Ketchup 500g', 'Potato Chips 150g', 'Mineral Water 1L', 'Besan 1kg', 'Poha 1kg', 'Suji 1kg', 'Mango Pickle 500g', 'Turmeric Powder 200g', 'Garam Masala 100g', 'Toor Dal 1kg'], 'Vegetables': ['Potato 1kg', 'Onion 1kg', 'Tomato 1kg', 'Carrot 500g', 'Cabbage 1pc', 'Cauliflower 1pc', 'Spinach 1 bunch', 'Brinjal 500g', 'Green Capsicum 500g', 'Cucumber 500g', 'Lady Finger 500g', 'Green Peas 500g', 'Pumpkin 1kg', 'Bottle Gourd 1pc', 'Bitter Gourd 500g', 'French Beans 500g', 'Radish 500g', 'Beetroot 500g', 'Garlic 250g', 'Ginger 250g', 'Green Chilli 100g', 'Sweet Corn 2pcs', 'Broccoli 500g', 'Button Mushroom 200g', 'Drumstick 250g', 'Raw Banana 1kg', 'Fresh Coriander 1 bunch', 'Fresh Mint 1 bunch', 'Lemon 500g', 'Curry Leaves 100g'], 'Fruits': ['Royal Gala Apple 1kg', 'Banana Robusta 1 dozen', 'Alphonso Mango 1kg', 'Nagpur Orange 1kg', 'Green Grapes 500g', 'Pomegranate 1kg', 'Watermelon 1pc', 'Papaya 1pc', 'Allahabad Guava 1kg', 'Pineapple 1pc', 'Strawberry 250g', 'Kiwi 3pcs', 'Green Pear 1kg', 'Peach 500g', 'Plum 500g', 'Fresh Litchi 500g', 'Tender Coconut 1pc', 'Dragon Fruit 2pcs', 'Muskmelon 1pc', 'Chikoo 1kg', 'Hass Avocado 2pcs', 'Blueberry 125g', 'Raspberry 125g', 'Fresh Fig 250g', 'Premium Dates 500g', 'Jackfruit 1pc', 'Custard Apple 500g', 'Mosambi 1kg', 'Imported Fuji Apple 1kg', 'Kesar Mango 1kg'], 'Electronics': ['5G Android Smartphone', 'Flagship Smartphone 256GB', 'Gaming Laptop i7', 'Business Laptop i5', '10-inch Android Tablet', '43-inch 4K Smart TV', '55-inch QLED Smart TV', 'Portable Bluetooth Speaker', '5.1 Channel Soundbar', 'ANC Wireless Earbuds', 'AMOLED Smartwatch', 'Mirrorless Digital Camera', '20,000mAh Power Bank', '1TB NVMe SSD', '2TB External HDD', 'Dual Band WiFi Router', 'Wireless Multifunction Printer', 'Mechanical RGB Keyboard', 'Wireless Gaming Mouse', '1080p Webcam', '27-inch IPS Monitor', '1.5 Ton Inverter AC', 'Double Door Refrigerator', '8kg Front Load Washing Machine', 'Convection Microwave Oven', 'Digital Air Fryer', '750W Mixer Grinder', 'Cordless Vacuum Cleaner', 'RO Water Purifier', '4K Home Projector'], 'Fashion': ['Classic Men Cotton T-Shirt', 'Men Slim Fit Shirt', 'Men Stretch Jeans', 'Men Formal Trousers', 'Men Festive Kurta', 'Women Silk Saree', 'Women Cotton Kurti', 'Women Party Dress', 'Women Straight Jeans', 'Women Casual Top', 'Women Stretch Leggings', 'Kids Printed T-Shirt', 'Kids Denim Jeans', 'Unisex Winter Jacket', 'Oversized Hoodie', 'Fleece Sweatshirt', 'Men Sports Shoes', 'Women Running Shoes', 'Casual Sneakers', 'Comfort Sandals', 'Daily Wear Slippers', 'Women Handbag', 'Laptop Backpack', 'Leather Wallet', 'Classic Leather Belt', 'UV Sunglasses', 'Analog Wrist Watch', 'Cotton Baseball Cap', 'Winter Wool Scarf', 'Ethnic Kurta Set'], 'Kids & Baby': ['Newborn Bodysuit Set', 'Baby Feeding Bottle', 'Baby Diaper Pack S', 'Baby Diaper Pack M', 'Baby Diaper Pack L', 'Baby Diaper Pack XL', 'Baby Wet Wipes', 'Baby Shampoo', 'Baby Lotion', 'Baby Powder', 'Soft Plush Teddy', 'Musical Rattle Set', 'Teething Ring', 'Kids Building Blocks', 'Kids Drawing Kit', 'Remote Toy Car', 'Doll House Set', 'Kids School Backpack', 'Kids Water Bottle', 'Kids Lunch Box', 'Coloring Book Set', 'Crayon Pack', 'Kids Puzzle 100pc', 'Educational Flash Cards', 'Kids Story Book', 'Boys Festive Kurta', 'Girls Party Frock', 'Kids Sports Shoes', 'Baby Blanket', 'Kids Study Table'], 'Dairy': ['Full Cream Milk 1L', 'Toned Milk 1L', 'Double Toned Milk 1L', 'Fresh Curd 500g', 'Greek Yogurt 400g', 'Mango Yogurt 100g', 'Strawberry Yogurt 100g', 'Fresh Paneer 200g', 'Malai Paneer 200g', 'Cheese Slices 200g', 'Mozzarella Cheese 200g', 'Butter 500g', 'Salted Butter 100g', 'Fresh Cream 200ml', 'Flavoured Lassi 250ml', 'Plain Lassi 250ml', 'Buttermilk 500ml', 'Chocolate Milk 200ml', 'Badam Milk 200ml', 'Milk Powder 500g', 'Condensed Milk 400g', 'Cheese Spread 200g', 'Cottage Cheese Cubes 200g', 'Fresh Khoya 250g', 'Vanilla Ice Cream 1L', 'Chocolate Ice Cream 1L', 'Strawberry Ice Cream 1L', 'Kulfi Family Pack', 'Dairy Whitener 500g', 'Probiotic Curd 400g'], 'Meat & Fish': ['Fresh Chicken Curry Cut 500g', 'Chicken Breast 500g', 'Chicken Leg 500g', 'Chicken Wings 500g', 'Chicken Keema 500g', 'Mutton Curry Cut 500g', 'Mutton Boneless 500g', 'Mutton Keema 500g', 'Rohu Fish 1kg', 'Katla Fish 1kg', 'Hilsa Fish 1kg', 'Prawns Medium 500g', 'Pomfret Fish 500g', 'Crab 1kg', 'Surmai Fish 500g', 'Bhetki Fillet 500g', 'Basa Fillet 500g', 'Tuna Steak 500g', 'Salmon Fillet 250g', 'Fish Fry Cut 500g', 'Fish Curry Cut 500g', 'Chicken Sausage 500g', 'Chicken Salami 250g', 'Eggs Farm Fresh 12pcs', 'Eggs Brown 12pcs', 'Quail Eggs 12pcs', 'Frozen Chicken Nuggets 500g', 'Frozen Fish Fingers 400g', 'Mutton Seekh Kebab 500g', 'Chicken Seekh Kebab 500g'], 'Beauty & Personal Care': ['Vitamin C Face Wash', 'Aloe Vera Face Wash', 'Hydrating Face Cream', 'Matte Sunscreen SPF 50', 'Aloe Vera Gel', 'Rose Water Toner', 'Anti-Dandruff Shampoo', 'Keratin Shampoo', 'Daily Conditioner', 'Hair Serum', 'Coconut Hair Oil', 'Body Wash', 'Moisturizing Body Lotion', 'Hand Wash Refill', 'Liquid Hand Sanitizer', 'Herbal Toothpaste', 'Whitening Toothpaste', 'Soft Toothbrush Pack', 'Lip Balm', 'Matte Lipstick', 'Kajal Eyeliner', 'Liquid Foundation', 'Compact Powder', 'Makeup Brush Set', 'Face Sheet Mask', 'Beard Trimmer', 'Men Face Wash', 'Deodorant Spray', 'Perfume Eau de Parfum', 'Bath Soap Pack'], 'Home & Kitchen': ['Non-Stick Fry Pan 24cm', 'Hard Anodized Kadai', 'Stainless Steel Pressure Cooker', 'Electric Kettle 1.5L', '750W Mixer Grinder', '4-Slice Toaster', 'Digital Kitchen Scale', 'Hand Blender', 'Rice Cooker 1.8L', 'Air Fryer 4L', 'Dinner Set 24pc', 'Stainless Steel Bottle 1L', 'Glass Storage Jar Set', 'Airtight Container Set', 'Lunch Box 3-Tier', 'Chopping Board', 'Chef Knife', 'Kitchen Tool Set', 'Silicone Spatula Set', 'Tea Cup Set', 'Bedsheet King Size', 'Cotton Pillow Cover Set', 'Memory Foam Pillow', 'Microfiber Towel Set', 'LED Table Lamp', 'Curtain Pair', 'Floor Mat', 'Laundry Basket', 'Storage Organizer Box', 'Vacuum Storage Bag Set'], 'Books & Stationery': ['A4 Notebook 200 Pages', 'Hardbound Diary', 'Ball Pen Pack', 'Gel Pen Pack', 'Mechanical Pencil Set', 'HB Pencil Pack', 'Highlighter Set', 'Permanent Marker Pack', 'A4 Printer Paper 500 Sheets', 'Sticky Notes Set', 'Geometry Box', 'Scientific Calculator', 'Drawing Book A4', 'Watercolor Set', 'Sketch Pen Set', 'Craft Paper Pack', 'File Folder Set', 'Document Organizer', 'Whiteboard Marker Set', 'Whiteboard 2x3ft', 'Academic Planner', 'To-Do Planner', 'English Grammar Book', 'General Knowledge Book', 'Competitive Maths Guide', 'Python Programming Book', 'Data Structures Book', 'Computer Networks Book', 'Novel Bestseller Edition', 'Kids Activity Book'], 'Sports & Fitness': ['Yoga Mat 6mm', 'Resistance Band Set', 'Adjustable Dumbbell Pair', 'Kettlebell 8kg', 'Skipping Rope', 'Pull Up Bar', 'Gym Gloves', 'Wrist Support Pair', 'Ankle Support Pair', 'Treadmill Foldable', 'Exercise Cycle', 'Cricket Bat English Willow', 'Cricket Ball Leather', 'Cricket Stumps Set', 'Football Size 5', 'Basketball Size 7', 'Volleyball', 'Badminton Racket Pair', 'Shuttlecock Tube', 'Table Tennis Bat Pair', 'TT Ball Pack', 'Carrom Board', 'Chess Set', 'Yoga Block Pair', 'Foam Roller', 'Gym Water Bottle', 'Fitness Smart Band', 'Sports Cap', 'Running Knee Sleeve', 'Camping Backpack'], 'Mobile Accessories': ['65W Fast Charger', '25W Type-C Charger', 'USB-C Cable 1m', 'USB-C Cable 2m', 'Lightning Cable', '3-in-1 Charging Cable', '20W Power Adapter', 'MagSafe Power Bank', 'Wireless Charging Pad', 'Car Phone Holder', 'Desktop Phone Stand', 'Ring Light 10-inch', 'Bluetooth Selfie Stick', 'Tempered Glass Screen Guard', 'Privacy Screen Guard', 'Silicone Phone Case', 'Rugged Phone Case', 'Laptop Sleeve 15-inch', 'Type-C Hub 6-in-1', 'USB Flash Drive 128GB', 'OTG Adapter Type-C', 'Bluetooth Keyboard', 'Bluetooth Mouse', 'TWS Earbuds Case', 'Smartwatch Strap', 'Phone Cleaning Kit', 'Cable Organizer Set', 'Mini Tripod', 'Gaming Finger Sleeves', 'Mobile Cooling Fan'], 'Pet Supplies': ['Premium Dog Food 3kg', 'Adult Dog Food 3kg', 'Puppy Food 2kg', 'Cat Food 1.2kg', 'Kitten Food 1kg', 'Dog Treats 500g', 'Cat Treats 200g', 'Dental Chews Pack', 'Dog Shampoo', 'Cat Shampoo', 'Flea Control Spray', 'Pet Grooming Brush', 'Nail Clipper for Pets', 'Stainless Pet Bowl', 'Automatic Pet Feeder', 'Pet Water Fountain', 'Dog Leash', 'Dog Harness', 'Cat Collar', 'Pet ID Tag', 'Chew Toy Bone', 'Plush Pet Toy', 'Cat Scratching Post', 'Interactive Cat Toy', 'Pet Bed Small', 'Pet Bed Large', 'Travel Pet Carrier', 'Pet Waste Bags', 'Bird Seed Mix 1kg', 'Aquarium Fish Food 500g'], 'Automobile': ['Car Engine Oil 5W30', 'Car Engine Oil 10W40', 'Bike Engine Oil', 'Car Air Freshener', 'Dashboard Cleaner', 'Car Shampoo 1L', 'Microfiber Car Cloth Set', 'Car Cleaning Brush', 'Tyre Polish', 'Windshield Washer Fluid', 'Car Vacuum Cleaner', 'Portable Tyre Inflator', 'Digital Tyre Pressure Gauge', 'Jump Starter Power Bank', 'Car Battery Charger', 'USB Car Charger', 'Car Phone Mount', 'Seat Cushion', 'Steering Wheel Cover', 'Sunshade Pair', 'Car Floor Mat Set', 'Car Seat Cover Set', 'LED Headlight Bulb', 'Fog Lamp Pair', 'Bike Helmet', 'Bike Chain Lube', 'Bike Phone Mount', 'Motorcycle Gloves', 'Car Emergency Kit', 'Reflective Safety Triangle'], 'Jewellery': ['Gold Plated Chain', 'Gold Plated Earrings', 'Gold Plated Bracelet', 'Silver Chain', 'Silver Anklet Pair', 'Silver Stud Earrings', 'Pearl Necklace', 'Pearl Earrings', 'Artificial Diamond Ring', 'Solitaire Style Pendant', 'Kundan Necklace Set', 'Kundan Earrings', 'Oxidized Jhumka', 'Oxidized Necklace', 'Bridal Bangles Set', 'Glass Bangles Set', 'Charm Bracelet', 'Heart Pendant', 'Men Steel Bracelet', 'Men Chain Bracelet', 'Classic Cufflinks', 'Tie Pin Set', 'Fashion Brooch', 'Hair Jewellery Set', 'Maang Tikka', 'Nose Pin', 'Jewellery Box', 'Travel Jewellery Organizer', 'Crystal Stud Earrings', 'Layered Fashion Necklace'], 'Medicine & Health': ['Digital Thermometer', 'Pulse Oximeter', 'Digital BP Monitor', 'First Aid Kit', 'Hot Water Bag', 'Cold Gel Pack', 'Antiseptic Liquid', 'Cotton Roll Pack', 'Adhesive Bandage Pack', 'Medical Tape', 'Hand Sanitizer 500ml', 'Face Mask Pack', 'Steam Inhaler', 'Nebulizer Machine', 'Heating Pad', 'Knee Support', 'Back Support Belt', 'Wrist Brace', 'Elastic Crepe Bandage', 'Eye Drop Bottle Holder', 'Vitamin C Tablets', 'ORS Electrolyte Pack', 'Protein Nutrition Powder', 'Herbal Balm', 'Moisturizing Cream', 'Mosquito Repellent', 'Pain Relief Spray', 'Multivitamin Gummies', 'Glucose Powder', 'Health Journal'], 'Festival & Decoration': ['LED String Lights', 'Warm White Fairy Lights', 'Decorative Diyas Set', 'Brass Diya', 'Rangoli Colour Set', 'Rangoli Stencil Set', 'Flower Toran', 'Door Hanging Toran', 'Marigold Garland', 'Artificial Flower Garland', 'Festive Candle Set', 'Scented Candle Pack', 'Decorative Lantern', 'Paper Lantern Set', 'Balloon Decoration Kit', 'Birthday Banner', 'Party Table Decor', 'Gift Wrapping Paper', 'Premium Gift Box', 'Ribbon Roll Set', 'Puja Thali Set', 'Incense Stick Pack', 'Camphor Pack', 'Festive Wall Sticker', 'Mandala Wall Hanging', 'Artificial Marigold Flowers', 'Diwali Gift Hamper', 'Durga Puja Decoration Set', 'Ganpati Decoration Set', 'Navratri Decoration Set'], 'Gaming Zone': ['Gaming Console 1TB', 'Wireless Gaming Controller', 'RGB Gaming Headset', 'Mechanical Gaming Keyboard', 'Gaming Mouse 12000 DPI', 'Gaming Mouse Pad XL', 'Gaming Monitor 27-inch', 'Streaming Webcam', 'USB Microphone', 'RGB LED Strip', 'Gaming Chair', 'Gaming Desk', 'Console Cooling Stand', 'Controller Charging Dock', 'Racing Wheel Set', 'Gaming Steering Pedal Set', 'VR Headset', 'Portable Gamepad', 'PC Game Controller', 'Capture Card', 'Gaming SSD 1TB', 'Gaming RAM 16GB', 'Graphics Card 8GB', 'WiFi Gaming Router', 'Headset Stand', 'Controller Skin Set', 'Gaming Finger Sleeves', 'Arcade Joystick', 'Game Storage Case', 'RGB Cable Kit'], 'Smart AI Devices': ['AI Smart Speaker', 'AI Voice Assistant Display', 'Smart LED Bulb', 'Smart WiFi Plug', 'Smart Security Camera', 'Smart Door Sensor', 'Smart Motion Sensor', 'Smart Video Doorbell', 'Smart Door Lock', 'Smart IR Remote', 'Smart Air Purifier', 'Smart Robot Vacuum', 'Smart Temperature Sensor', 'Smart Humidity Sensor', 'Smart Smoke Detector', 'Smart Water Leak Sensor', 'Smart Light Strip', 'Smart Ceiling Light', 'Smart Curtain Controller', 'Smart Energy Meter', 'Smart WiFi Router', 'Smartwatch AI Edition', 'AI Noise Cancelling Earbuds', 'AI Translation Earbuds', 'AI Digital Photo Frame', 'Smart Pet Feeder', 'Smart Baby Monitor', 'Smart Plant Sensor', 'Smart Health Scale', 'Smart Home Hub']}
for c in CATS: BASE.setdefault(c,[f'{c} Product {i}' for i in range(1,31)])

def db():
 c=sqlite3.connect(DB,timeout=30,check_same_thread=False); c.row_factory=sqlite3.Row; c.execute('PRAGMA busy_timeout=30000'); return c

def hp(p):
 s=os.urandom(32); return s.hex(),hashlib.pbkdf2_hmac('sha256',p.encode(),s,310000).hex()
def vp(p,s,d):
 try:return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),310000).hex(),d)
 except:return False
def now():return datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

def dt_ist(s):
 try:return datetime.strptime(s,'%Y-%m-%d %H:%M:%S').replace(tzinfo=IST)
 except:return datetime.now(IST)

def fmt_ist(s):
 try:return dt_ist(s).strftime('%d %b %Y, %I:%M %p IST')
 except:return s

def _slug_image(s):
 return re.sub(r"[^a-z0-9]+","_",str(s).lower()).strip("_")

IMAGE_ROOT=Path(__file__).parent / "images"

@lru_cache(maxsize=700)
def product_image(name, category):
 # Every catalog item has a bundled local product visual, so images do not
 # depend on an external image host and continue working on Streamlit Cloud.
 cat=category or ""
 path=None
 if cat:
  candidate_dir=IMAGE_ROOT / _slug_image(cat)
  if candidate_dir.exists():
   for f in candidate_dir.glob(f"*_{_slug_image(name)}.svg"):
    path=f; break
 if path is None:
  # Used by order/cart screens where only the product name is available.
  for c in CATS:
   candidate_dir=IMAGE_ROOT / _slug_image(c)
   if candidate_dir.exists():
    for f in candidate_dir.glob(f"*_{_slug_image(name)}.svg"):
     path=f; break
    if path: break
 if path and path.exists():
  raw=base64.b64encode(path.read_bytes()).decode("ascii")
  return "data:image/svg+xml;base64," + raw
 # Final fallback for any future admin-created product.
 q=quote(f"{name} {category} product")
 return f"https://loremflickr.com/700/700/{q}?lock={abs(hash(str(category)+"|"+str(name)))%100000}"

def money(x):return f'₹{x:,.2f}'

def setup():
 c=db(); c.executescript('''
 CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT UNIQUE,phone TEXT,salt TEXT,phash TEXT,role TEXT DEFAULT 'customer',wallet REAL DEFAULT 0,rewards INTEGER DEFAULT 0,vip INTEGER DEFAULT 0,created TEXT);
 CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY,name TEXT,category TEXT,price REAL,stock INTEGER DEFAULT 0,sold INTEGER DEFAULT 0,rating REAL DEFAULT 4.2);
 CREATE TABLE IF NOT EXISTS carts(id INTEGER PRIMARY KEY,user_id INTEGER UNIQUE,created TEXT);
 CREATE TABLE IF NOT EXISTS cart_items(id INTEGER PRIMARY KEY,cart_id INTEGER,product_id INTEGER,qty INTEGER,UNIQUE(cart_id,product_id));
 CREATE TABLE IF NOT EXISTS wishlist(user_id INTEGER,product_id INTEGER,UNIQUE(user_id,product_id));
 CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,user_id INTEGER,subtotal REAL,discount REAL,fee REAL,total REAL,method TEXT,status TEXT,created TEXT,cb_pct REAL,cb_amt REAL,cb_done INTEGER DEFAULT 0,tracking TEXT,expected_delivery TEXT,came_to_store_at TEXT,packed_at TEXT,out_for_delivery_at TEXT);
 CREATE TABLE IF NOT EXISTS order_items(order_id INTEGER,product_id INTEGER,qty INTEGER,price REAL);
 CREATE TABLE IF NOT EXISTS wallet_tx(id INTEGER PRIMARY KEY,user_id INTEGER,amount REAL,kind TEXT,created TEXT);
 CREATE TABLE IF NOT EXISTS tracking(id INTEGER PRIMARY KEY,order_id INTEGER,status TEXT,created TEXT);
 CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,user_id INTEGER,product_id INTEGER,rating INTEGER,review TEXT,created TEXT,UNIQUE(user_id,product_id));
 CREATE TABLE IF NOT EXISTS addresses(id INTEGER PRIMARY KEY,user_id INTEGER,label TEXT,address TEXT,city TEXT,state TEXT,pincode TEXT,phone TEXT,created TEXT);
 CREATE TABLE IF NOT EXISTS reward_events(id INTEGER PRIMARY KEY,user_id INTEGER,points INTEGER,kind TEXT,created TEXT);
 CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY,user_id INTEGER,title TEXT,body TEXT,created TEXT,read INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS support_messages(id INTEGER PRIMARY KEY,user_id INTEGER,role TEXT,message TEXT,created TEXT);
 ''')
 ensure_order_columns(c)
 # Migrate older generic listings such as "Dairy Product 15" to the new named catalog.
 for cat,names in BASE.items():
  for i,n in enumerate(names[:30],1):
   old_name=f'{cat} Product {i}'
   old=c.execute('SELECT id FROM products WHERE name=? AND category=?',(old_name,cat)).fetchone()
   target=c.execute('SELECT id FROM products WHERE name=? AND category=?',(n,cat)).fetchone()
   if old and not target:
    c.execute('UPDATE products SET name=? WHERE id=?',(n,old['id']))
   elif old and target and old['id']!=target['id']:
    old_id,target_id=old['id'],target['id']
    # Preserve customer data when consolidating an old generic listing.
    old_cart=c.execute('SELECT cart_id,qty FROM cart_items WHERE product_id=?',(old_id,)).fetchall()
    for ci in old_cart:
     existing=c.execute('SELECT id,qty FROM cart_items WHERE cart_id=? AND product_id=?',(ci['cart_id'],target_id)).fetchone()
     if existing:
      c.execute('UPDATE cart_items SET qty=qty+? WHERE id=?',(ci['qty'],existing['id']))
      c.execute('DELETE FROM cart_items WHERE id=?',(ci['id'],))
     else:c.execute('UPDATE cart_items SET product_id=? WHERE id=?',(target_id,ci['id']))
    c.execute('INSERT OR IGNORE INTO wishlist(user_id,product_id) SELECT user_id,? FROM wishlist WHERE product_id=?',(target_id,old_id))
    c.execute('DELETE FROM wishlist WHERE product_id=?',(old_id,))
    c.execute('UPDATE order_items SET product_id=? WHERE product_id=?',(target_id,old_id))
    c.execute('UPDATE reviews SET product_id=? WHERE product_id=?',(target_id,old_id))
    c.execute('DELETE FROM products WHERE id=?',(old_id,))
   if not c.execute('SELECT 1 FROM products WHERE name=? AND category=?',(n,cat)).fetchone():
    c.execute('INSERT INTO products(name,category,price,stock,sold,rating) VALUES(?,?,?,?,?,?)',(n,cat,round(49+((i*137+len(cat)*31)%1900),2),25+(i*7)%90,i*2,round(4+(i%10)/10,1)))
 for email,name,pwd,role in [('admin@bharatmart.com','BharatMart Admin','BM_Admin_2026!','admin'),('customer@bharatmart.com','BharatMart Customer','BM_Customer_2026!','customer')]:
  u=c.execute('SELECT * FROM users WHERE lower(email)=lower(?)',(email,)).fetchone(); s,d=hp(pwd)
  if u:
   c.execute('UPDATE users SET salt=?,phash=?,role=? WHERE id=?',(s,d,role,u['id']))
   uid=u['id']
   if role=='customer' and u['wallet']==0:
    c.execute('UPDATE users SET wallet=? WHERE id=?',(START,uid)); c.execute('INSERT INTO wallet_tx(user_id,amount,kind,created) VALUES(?,?,?,?)',(uid,START,'WELCOME ₹100 CRORE VIRTUAL CASH',now()))
  else:
   c.execute('INSERT INTO users(name,email,salt,phash,role,wallet,created) VALUES(?,?,?,?,?,?,?)',(name,email,s,d,role,START if role=='customer' else 0,now())); uid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
   if role=='customer': c.execute('INSERT INTO wallet_tx(user_id,amount,kind,created) VALUES(?,?,?,?)',(uid,START,'WELCOME ₹100 CRORE VIRTUAL CASH',now()))
  c.execute('INSERT OR IGNORE INTO carts(user_id,created) VALUES(?,?)',(uid,now()))
 # Backfill scheduling fields for older orders without changing their existing status.
 for old in c.execute('SELECT id,created,expected_delivery,came_to_store_at,packed_at,out_for_delivery_at FROM orders').fetchall():
  if not old['expected_delivery']:
   cd=dt_ist(old['created']); days=random.randint(5,7)
   c.execute('UPDATE orders SET came_to_store_at=?,packed_at=?,out_for_delivery_at=?,expected_delivery=? WHERE id=?',(
    (cd+timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),(cd+timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),(cd+timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),(cd+timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S'),old['id']))
 c.commit();c.close()

def login(e,p):
 c=db();u=c.execute('SELECT * FROM users WHERE lower(email)=lower(?)',(e.strip(),)).fetchone(); ok=bool(u and vp(p,u['salt'],u['phash'])); c.close(); return dict(u) if ok else None

def register(n,e,ph,p):
 c=db()
 if c.execute('SELECT 1 FROM users WHERE lower(email)=lower(?)',(e.strip(),)).fetchone():c.close();return False,'Email already exists.'
 s,d=hp(p);c.execute('INSERT INTO users(name,email,phone,salt,phash,wallet,created) VALUES(?,?,?,?,?,?,?)',(n.strip(),e.strip().lower(),ph,s,d,START,now()));uid=c.execute('SELECT last_insert_rowid()').fetchone()[0];c.execute('INSERT INTO carts(user_id,created) VALUES(?,?)',(uid,now()));c.execute('INSERT INTO wallet_tx(user_id,amount,kind,created) VALUES(?,?,?,?)',(uid,START,'WELCOME ₹100 CRORE VIRTUAL CASH',now()));c.commit();c.close();return True,'Account created with ₹100 crore virtual cash.'

def add(uid,pid):
 c=db();cid=c.execute('SELECT id FROM carts WHERE user_id=?',(uid,)).fetchone()['id'];c.execute('INSERT INTO cart_items(cart_id,product_id,qty) VALUES(?,?,1) ON CONFLICT(cart_id,product_id) DO UPDATE SET qty=qty+1',(cid,pid));c.commit();c.close()
def cart(uid):
 c=db();r=c.execute('SELECT ci.product_id,ci.qty,p.name,p.price,p.stock FROM cart_items ci JOIN carts ca ON ca.id=ci.cart_id JOIN products p ON p.id=ci.product_id WHERE ca.user_id=?',(uid,)).fetchall();c.close();return [dict(x) for x in r]
def remove(uid,pid):
 c=db();c.execute('DELETE FROM cart_items WHERE product_id=? AND cart_id=(SELECT id FROM carts WHERE user_id=?)',(pid,uid));c.commit();c.close()
def ensure_order_columns(c):
 cols={r['name'] for r in c.execute('PRAGMA table_info(orders)').fetchall()}
 for col in ['expected_delivery','came_to_store_at','packed_at','out_for_delivery_at']:
  if col not in cols:c.execute(f'ALTER TABLE orders ADD COLUMN {col} TEXT')

def step_status(o):
 if o['status']=='CANCELLED':return 'CANCELLED'
 created=dt_ist(o['created']); nowdt=datetime.now(IST)
 expected=o['expected_delivery']
 if expected and nowdt>=dt_ist(expected):return 'DELIVERED'
 if o['out_for_delivery_at'] and nowdt>=dt_ist(o['out_for_delivery_at']):return 'OUT FOR DELIVERY'
 if o['packed_at'] and nowdt>=dt_ist(o['packed_at']):return 'PACKED'
 if o['came_to_store_at'] and nowdt>=dt_ist(o['came_to_store_at']):return 'CAME TO STORE'
 return 'ORDER PLACED'
def sync(oid):
 c=db();o=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone();
 if not o:c.close();return
 ns=step_status(o)
 if ns!=o['status']:
  c.execute('UPDATE orders SET status=? WHERE id=?',(ns,oid));c.execute('INSERT INTO tracking(order_id,status,created) VALUES(?,?,?)',(oid,ns,now()))
  if ns=='DELIVERED' and not o['cb_done']:
   c.execute('UPDATE users SET wallet=wallet+? WHERE id=?',(o['cb_amt'],o['user_id']));c.execute('INSERT INTO wallet_tx(user_id,amount,kind,created) VALUES(?,?,?,?)',(o['user_id'],o['cb_amt'],f'CASHBACK ORDER #{oid}',now()));c.execute('UPDATE orders SET cb_done=1 WHERE id=?',(oid,))
 c.commit();c.close()
def force_next(oid):
 c=db();o=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone();
 if not o or o['status'] not in STEPS:c.close();return
 ns=STEPS[min(STEPS.index(o['status'])+1,4)];c.execute('UPDATE orders SET status=? WHERE id=?',(ns,oid));c.execute('INSERT INTO tracking(order_id,status,created) VALUES(?,?,?)',(oid,ns,now()))
 if ns=='DELIVERED' and not o['cb_done']:
  c.execute('UPDATE users SET wallet=wallet+? WHERE id=?',(o['cb_amt'],o['user_id']));c.execute('INSERT INTO wallet_tx(user_id,amount,kind,created) VALUES(?,?,?,?)',(o['user_id'],o['cb_amt'],f'CASHBACK ORDER #{oid}',now()));c.execute('UPDATE orders SET cb_done=1 WHERE id=?',(oid,))
 c.commit();c.close()

def place(uid,method,coupon):
 c=db();rows=c.execute('SELECT ci.product_id,ci.qty,p.name,p.price,p.stock FROM cart_items ci JOIN carts ca ON ca.id=ci.cart_id JOIN products p ON p.id=ci.product_id WHERE ca.user_id=?',(uid,)).fetchall()
 if not rows:c.close();return None,'Cart is empty.'
 if any(x['qty']>x['stock'] for x in rows):c.close();return None,'Insufficient stock.'
 sub=sum(x['price']*x['qty'] for x in rows);disc=0
 if coupon.upper()=='WELCOME10' and sub>=500:disc=min(sub*.10,300)
 elif coupon.upper()=='FESTIVE20' and sub>=1500:disc=min(sub*.20,500)
 elif coupon.upper()=='MEGASALE50' and sub>=5000:disc=min(sub*.50,25000)
 elif coupon.strip() and coupon.upper() not in ('WELCOME10','FESTIVE20','MEGASALE50'):c.close();return None,'Invalid coupon.'
 fee=0 if sub-disc>=500 else 49;total=round(sub-disc+fee,2);u=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
 if method=='Virtual Wallet' and u['wallet']<total:c.close();return None,'Insufficient virtual wallet balance.'
 cbp=random.randint(20,50)+(5 if u['vip'] else 0);cbp=max(cbp,50) if coupon.upper()=='MEGASALE50' else cbp;cba=round(total*cbp/100,2);created=now(); created_dt=dt_ist(created); delivery_days=random.randint(5,7)
 came=(created_dt+timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'); packed=(created_dt+timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'); out=(created_dt+timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'); expected=(created_dt+timedelta(days=delivery_days)).strftime('%Y-%m-%d %H:%M:%S')
 track='BM'+created_dt.strftime('%Y%m%d')+str(random.randint(100000,999999))
 c.execute('INSERT INTO orders(user_id,subtotal,discount,fee,total,method,status,created,cb_pct,cb_amt,tracking,expected_delivery,came_to_store_at,packed_at,out_for_delivery_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uid,sub,disc,fee,total,method,'ORDER PLACED',created,cbp,cba,track,expected,came,packed,out));oid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
 for x in rows:c.execute('INSERT INTO order_items(order_id,product_id,qty,price) VALUES(?,?,?,?)',(oid,x['product_id'],x['qty'],x['price']));c.execute('UPDATE products SET stock=stock-?,sold=sold+? WHERE id=?',(x['qty'],x['qty'],x['product_id']))
 if method=='Virtual Wallet':c.execute('UPDATE users SET wallet=wallet-? WHERE id=?',(total,uid));c.execute('INSERT INTO wallet_tx(user_id,amount,kind,created) VALUES(?,?,?,?)',(uid,-total,f'ORDER #{oid} PAYMENT',created))
 c.execute('INSERT INTO tracking(order_id,status,created) VALUES(?,?,?)',(oid,'ORDER PLACED',created));c.execute('DELETE FROM cart_items WHERE cart_id=(SELECT id FROM carts WHERE user_id=?)',(uid,));c.commit();c.close();return oid,None

CATEGORY_ICONS={'Grocery': '🛒', 'Vegetables': '🥦', 'Fruits': '🍎', 'Electronics': '📱', 'Fashion': '👕', 'Kids & Baby': '🧸', 'Dairy': '🥛', 'Meat & Fish': '🐟', 'Beauty & Personal Care': '💄', 'Home & Kitchen': '🏠', 'Books & Stationery': '📚', 'Sports & Fitness': '🏋️', 'Mobile Accessories': '🔌', 'Pet Supplies': '🐾', 'Automobile': '🚗', 'Jewellery': '💎', 'Medicine & Health': '🩺', 'Festival & Decoration': '🎉', 'Gaming Zone': '🎮', 'Smart AI Devices': '🤖'}

def seller_for(category):
    groups={
        'Grocery':'BharatFresh','Vegetables':'BharatFresh','Fruits':'BharatFresh','Dairy':'BharatFresh',
        'Electronics':'Bharat Electronics','Mobile Accessories':'Bharat Electronics','Smart AI Devices':'Bharat Electronics','Gaming Zone':'Bharat Gaming',
        'Fashion':'Bharat Fashion','Kids & Baby':'Bharat Fashion','Beauty & Personal Care':'Bharat Beauty',
        'Home & Kitchen':'Bharat Home','Books & Stationery':'Bharat Books','Sports & Fitness':'Bharat Sports',
        'Pet Supplies':'Bharat Pets','Automobile':'Bharat Auto','Jewellery':'Bharat Luxe','Medicine & Health':'Bharat Care',
        'Festival & Decoration':'Bharat Celebrations','Meat & Fish':'Bharat FreshCatch'}
    return groups.get(category,'BharatMart Marketplace')

def product_rows(uid, limit=120, category='All', query='', sort='Popular'):
    c=db();sql='SELECT * FROM products WHERE 1=1';args=[]
    if category!='All':sql+=' AND category=?';args.append(category)
    if query:sql+=' AND (name LIKE ? OR category LIKE ?)';args += [f'%{query}%',f'%{query}%']
    order={'Low Price':'price ASC','High Price':'price DESC','Rating':'rating DESC,sold DESC','Newest':'id DESC'}.get(sort,'sold DESC,rating DESC')
    sql+=f' ORDER BY {order} LIMIT ?';args.append(limit)
    rows=c.execute(sql,args).fetchall();c.close();return rows

def add_reward(uid,points,kind):
    c=db();c.execute('UPDATE users SET rewards=rewards+? WHERE id=?',(points,uid));c.execute('INSERT INTO reward_events(user_id,points,kind,created) VALUES(?,?,?,?)',(uid,points,kind,now()));c.commit();c.close()

def save_address(uid,label,address,city,state,pincode,phone):
    c=db();c.execute('INSERT INTO addresses(user_id,label,address,city,state,pincode,phone,created) VALUES(?,?,?,?,?,?,?,?)',(uid,label,address,city,state,pincode,phone,now()));c.commit();c.close()

def get_addresses(uid):
    c=db();r=c.execute('SELECT * FROM addresses WHERE user_id=? ORDER BY id DESC',(uid,)).fetchall();c.close();return r

def notify(uid,title,body):
    c=db();c.execute('INSERT INTO notifications(user_id,title,body,created) VALUES(?,?,?,?)',(uid,title,body,now()));c.commit();c.close()

def recommendations(uid,limit=8):
    c=db()
    fav=c.execute('SELECT p.category FROM cart_items ci JOIN carts ca ON ca.id=ci.cart_id JOIN products p ON p.id=ci.product_id WHERE ca.user_id=? ORDER BY ci.id DESC LIMIT 5',(uid,)).fetchall()
    if fav:
        cats=list(dict.fromkeys([x['category'] for x in fav]));ph=','.join('?'*len(cats));r=c.execute(f'SELECT * FROM products WHERE category IN ({ph}) ORDER BY rating DESC,sold DESC LIMIT ?',cats+[limit]).fetchall()
    else:r=c.execute('SELECT * FROM products ORDER BY rating DESC,sold DESC LIMIT ?',(limit,)).fetchall()
    c.close();return r

def smart_answer(uid,text,budget=None):
    q=(text or '').lower();rows=[]
    category=None
    for cat in CATS:
        if cat.lower() in q or cat.split()[0].lower() in q:category=cat;break
    keywords={'yogurt':'Dairy','milk':'Dairy','paneer':'Dairy','rice':'Grocery','atta':'Grocery','vegetable':'Vegetables','fruit':'Fruits','phone':'Electronics','laptop':'Electronics','shirt':'Fashion','saree':'Fashion','shoe':'Fashion','baby':'Kids & Baby','makeup':'Beauty & Personal Care','shampoo':'Beauty & Personal Care','kitchen':'Home & Kitchen','book':'Books & Stationery','cricket':'Sports & Fitness','gym':'Sports & Fitness','charger':'Mobile Accessories','pet':'Pet Supplies','car':'Automobile','jewellery':'Jewellery','medicine':'Medicine & Health','gaming':'Gaming Zone','smartwatch':'Smart AI Devices'}
    for k,v in keywords.items():
        if k in q: category=v; break
    c=db();sql='SELECT * FROM products WHERE 1=1';args=[]
    if category:sql+=' AND category=?';args.append(category)
    terms=[t for t in q.replace(',',' ').split() if len(t)>2 and t not in {'under','with','for','the','and','want','need','from','best','show','give'}]
    if terms:
        like=[]
        for t in terms:like.append('(lower(name) LIKE ? OR lower(category) LIKE ?)');args += [f'%{t}%',f'%{t}%']
        sql+=' AND ('+' OR '.join(like)+')'
    sql+=' ORDER BY rating DESC,sold DESC LIMIT 8'
    try: rows=c.execute(sql,args).fetchall()
    except Exception: rows=[]
    if not rows and category: rows=c.execute('SELECT * FROM products WHERE category=? ORDER BY rating DESC,sold DESC LIMIT 8',(category,)).fetchall()
    c.close()
    if budget:
        rows=[r for r in rows if r['price']<=budget] or rows[:4]
    return rows,category

def product_card(uid,x,i,prefix='shop',compact=False):
    discount=12+(x['id']%36);old=round(x['price']/(1-discount/100),2);seller=seller_for(x['category'])
    if compact:
        st.markdown(f'<div class="bm-mini-card"><div class="bm-number">#{x["id"]} • {x["category"]}</div><img src="{product_image(x["name"],x["category"])}"><b>{x["name"]}</b><div>⭐ {x["rating"]:.1f} • {money(x["price"])}</div></div>',unsafe_allow_html=True)
    else:
        st.markdown(f'''<div class="bm-product"><div class="bm-product-top"><span class="bm-sale">-{discount}%</span><span class="bm-heart">♡</span></div><img src="{product_image(x["name"],x["category"])}"><div class="bm-number">PRODUCT #{x["id"]} • {x["category"].upper()}</div><div class="bm-product-name">{x["name"]}</div><div class="bm-rating">⭐ {x["rating"]:.1f} <span>• {x["sold"]:,} sold</span></div><div><span class="bm-price">{money(x["price"])}</span> <span class="bm-old">{money(old)}</span></div><div class="bm-seller">🏪 {seller} • BharatMart Fulfilled</div><div class="bm-stock">● {x["stock"]} available • +₹{max(5,int(x["price"]*.05))} cashback</div></div>''',unsafe_allow_html=True)
    b1,b2=st.columns(2)
    if b1.button('🛒 ADD TO CART',key=f'{prefix}_add_{x["id"]}_{i}',disabled=x['stock']<1,use_container_width=True):
        add(uid,x['id']);add_reward(uid,2,'Added product to cart');notify(uid,'🛒 Added to cart',f'{x["name"]} is ready in your cart.');st.toast(f'{x["name"]} added to cart')
    if b2.button('♡ SAVE',key=f'{prefix}_wish_{x["id"]}_{i}',use_container_width=True):
        c=db();c.execute('INSERT OR IGNORE INTO wishlist(user_id,product_id) VALUES(?,?)',(uid,x['id']));c.commit();c.close();add_reward(uid,1,'Saved to wishlist');st.toast('Saved to wishlist')

def main():
    st.set_page_config(page_title='BHARATMART MEGA MALL',page_icon='🛒',layout='wide',initial_sidebar_state='expanded')
    setup()
    st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');
:root{--navy:#06152d;--navy2:#0d3767;--orange:#ff6500;--gold:#ffb52e;--ink:#172033;--muted:#667085;--line:#e7edf4;--bg:#f4f7fb;--green:#159a5b;--red:#e34b4b}
html,body,[class*="css"]{font-family:Inter,sans-serif}.stApp{background:radial-gradient(circle at 90% 0%,#fff4e7 0,transparent 25%),radial-gradient(circle at 0% 40%,#eaf5ff 0,transparent 23%),linear-gradient(180deg,#f8fafc,#eef3f8)}.block-container{max-width:1560px;padding:1rem 1.35rem 4rem}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#031027,#092c55 65%,#0e416f);border-right:1px solid #173c63}section[data-testid="stSidebar"] *{color:#f7fbff!important}
.bm-top{background:linear-gradient(105deg,#031027,#0a315d 62%,#173f70);border-radius:27px;padding:16px 22px;color:#fff;box-shadow:0 20px 55px rgba(4,19,43,.2);margin-bottom:14px}.bm-brand{font-family:Poppins;font-size:31px;font-weight:800}.bm-brand span{color:#ff8a00}.bm-tag{font-size:9px;letter-spacing:3px;color:#a9bfd8}.bm-live{float:right;background:rgba(31,201,120,.14);border:1px solid rgba(145,255,198,.2);padding:6px 11px;border-radius:99px;font-size:10px;color:#caffdf}
.bm-hero{min-height:325px;border-radius:32px;padding:36px 42px;background:linear-gradient(120deg,#02132d 0%,#0b315e 56%,#ff6500 160%);color:#fff;position:relative;overflow:hidden;box-shadow:0 28px 70px rgba(5,24,50,.24);margin-bottom:18px}.bm-hero:before{content:"";position:absolute;right:-120px;bottom:-250px;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,rgba(255,181,46,.42),rgba(255,101,0,.04) 64%,transparent 70%)}.bm-hero:after{content:"";position:absolute;right:75px;top:-130px;width:260px;height:260px;border:48px solid rgba(255,255,255,.055);border-radius:50%}.bm-hero h1{font-family:Poppins;font-size:49px;line-height:1.02;margin:15px 0 10px;font-weight:800;position:relative;z-index:2}.bm-hero p{max-width:780px;color:#dce8f7;font-size:15px;line-height:1.7;position:relative;z-index:2}.bm-chip{display:inline-block;padding:7px 12px;border-radius:99px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.13);margin:3px 5px 0 0;font-size:10px;position:relative;z-index:2}.bm-cta{display:inline-block;background:linear-gradient(90deg,#ff6200,#ffb52e);padding:13px 19px;border-radius:13px;font-weight:800;margin-top:11px;position:relative;z-index:2;box-shadow:0 9px 28px rgba(255,101,0,.3)}
.bm-section{font-family:Poppins;font-size:25px;font-weight:800;color:var(--ink);margin:27px 0 10px}.bm-sub{color:var(--muted);font-size:13px;margin:-5px 0 14px}.bm-strip{display:flex;gap:10px;overflow:hidden;margin:12px 0 20px}.bm-pill{background:#fff;border:1px solid var(--line);border-radius:14px;padding:11px 14px;box-shadow:0 5px 18px rgba(16,24,40,.045);font-size:12px;white-space:nowrap}.bm-pill b{color:#ff6500}
.bm-trust{background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px;text-align:center;height:100%;box-shadow:0 7px 23px rgba(16,24,40,.045)}.bm-cat-tile{background:linear-gradient(145deg,#fff,#f8fbff);border:1px solid #e3eaf2;border-radius:19px;padding:16px;text-align:center;min-height:126px;box-shadow:0 7px 22px rgba(16,24,40,.045);transition:.18s}.bm-cat-tile:hover{transform:translateY(-5px);box-shadow:0 17px 38px rgba(16,24,40,.11);border-color:#ffd2b4}.bm-cat-icon{font-size:32px}.bm-cat{font-size:14px;font-weight:800;color:#182338}.bm-small{color:#68758a;font-size:11px}
.bm-product{background:rgba(255,255,255,.98);border:1px solid #e3eaf2;border-radius:21px;padding:13px;box-shadow:0 8px 28px rgba(16,24,40,.055);height:100%;transition:.2s;overflow:hidden}.bm-product:hover{transform:translateY(-5px);box-shadow:0 20px 42px rgba(16,24,40,.12)}.bm-product img{width:100%;height:210px;object-fit:cover;border-radius:15px;margin:7px 0 9px}.bm-product-top{display:flex;justify-content:space-between;align-items:center;height:24px}.bm-sale{background:#fff0e8;color:#df4e00;border-radius:8px;padding:5px 8px;font-size:9px;font-weight:900}.bm-heart{width:30px;height:30px;border-radius:50%;background:#f7f9fc;display:grid;place-items:center;font-size:20px}.bm-number{font-size:9px;color:#8994a5;font-weight:800;letter-spacing:.35px}.bm-product-name{font-size:15px;font-weight:850;color:#172033;margin:4px 0}.bm-rating{font-size:11px;color:#1c7d4e;font-weight:800;margin-bottom:5px}.bm-rating span{color:#8b96a6;font-weight:500}.bm-price{font-size:20px;font-weight:900;color:#101828}.bm-old{font-size:10px;color:#98a2b3;text-decoration:line-through}.bm-seller{font-size:10px;color:#667085;margin-top:7px}.bm-stock{color:#13814a;font-size:10px;font-weight:750;margin:5px 0 9px}.bm-badge{display:inline-block;padding:5px 8px;border-radius:8px;background:#fff1e8;color:#d94b00;font-size:9px;font-weight:800}.bm-mini-card{background:#fff;border:1px solid #e5ebf2;border-radius:17px;padding:10px;box-shadow:0 5px 18px rgba(16,24,40,.045)}.bm-mini-card img{width:100%;height:135px;object-fit:cover;border-radius:12px;margin:5px 0}.bm-mini-card b{font-size:12px}.bm-mini-card div:last-child{font-size:11px;margin-top:3px}
.bm-flash{background:linear-gradient(115deg,#210b08,#651d0e 55%,#ff6500);color:#fff;border-radius:25px;padding:22px;box-shadow:0 17px 44px rgba(140,42,12,.2);overflow:hidden}.bm-flash h2{font-family:Poppins;margin:0;font-size:27px}.bm-timer{font-family:Poppins;font-size:29px;font-weight:900;letter-spacing:2px}.bm-benefit{background:linear-gradient(145deg,#fff,#f7fbff);border:1px solid #e3eaf2;border-radius:21px;padding:20px;box-shadow:0 8px 24px rgba(16,24,40,.045)}.bm-wallet{background:linear-gradient(120deg,#03142e,#0c3d72);color:#fff;border-radius:25px;padding:24px;box-shadow:0 20px 48px rgba(5,28,57,.23)}.bm-wallet-value{font-family:Poppins;font-size:31px;font-weight:800}.bm-vip{background:linear-gradient(135deg,#17100a,#3d2509,#b26a05);color:#fff;border-radius:25px;padding:24px;box-shadow:0 20px 50px rgba(130,82,0,.18)}
div[data-testid="stMetric"]{background:#fff;border:1px solid #e6ebf2;padding:14px 16px;border-radius:16px;box-shadow:0 6px 20px rgba(16,24,40,.05)}.stButton>button{border-radius:11px;border:1px solid #d9e2ed;font-weight:800;min-height:40px;transition:.15s}.stButton>button:hover{border-color:#ff6500;color:#d94b00;transform:translateY(-1px)}.stButton>button[kind="primary"]{background:linear-gradient(90deg,#ff6500,#ff9d1c);border:0;color:#fff;box-shadow:0 8px 20px rgba(255,101,0,.22)}.stTextInput>div>div,.stSelectbox>div>div,.stTextArea>div>div{border-radius:11px}.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{font-weight:800}.stProgress>div>div{border-radius:99px}.bm-footer{margin-top:40px;padding:26px;border-radius:23px;background:#04132b;color:#cbd8e8;text-align:center}.bm-footer strong{color:#fff;font-family:Poppins;font-size:20px}.bm-track{padding:17px;border-radius:18px;background:#fff;border:1px solid #e5ebf2}.bm-track-line{height:5px;background:#e7edf4;border-radius:99px;margin:9px 0}.bm-score{font-family:Poppins;font-size:42px;font-weight:900;color:#ff6500}.bm-chat{background:#fff;border:1px solid #e2e9f1;border-radius:18px;padding:14px;box-shadow:0 6px 20px rgba(16,24,40,.05)}
@media(max-width:900px){.bm-hero h1{font-size:33px}.bm-hero{padding:25px;min-height:270px}.bm-brand{font-size:24px}.bm-live{display:none}.block-container{padding-left:.65rem;padding-right:.65rem}.bm-product img{height:160px}}
</style>''',unsafe_allow_html=True)

    st.markdown('<div class="bm-top"><span class="bm-live">● VIRTUAL MALL ONLINE</span><div class="bm-tag">SMART • DIGITAL • VIRTUAL COMMERCE</div><div class="bm-brand">BHARAT<span>MART</span> MEGA MALL</div><div style="font-size:12px;color:#dce8f7">India\'s smart virtual marketplace — discover, shop, earn.</div></div>',unsafe_allow_html=True)
    if 'user' not in st.session_state: st.session_state.user=None
    if not st.session_state.user:
        st.markdown('<div class="bm-hero"><span class="bm-chip">🇮🇳 MADE FOR INDIA</span><span class="bm-chip">💰 ₹100 CRORE VIRTUAL WALLET</span><span class="bm-chip">🎁 SMART CASHBACK</span><span class="bm-chip">🚚 5–7 DAY SIMULATED DELIVERY</span><h1>Shop More.<br>Save More. Earn More.</h1><p>A premium virtual mega mall with 20 departments, 600 named products, smart recommendations, flash deals, rewards, VIP membership and IST order tracking.</p><span class="bm-cta">⚡ ENTER BHARATMART</span></div>',unsafe_allow_html=True)
        trust=st.columns(4)
        for col,icon,title,sub in zip(trust,['🛡️','⚡','🎁','👑'],['Virtual & Safe','Flash Deals','Cashback Rewards','VIP Experience'],['Demo commerce only','Limited-time style offers','Earn on activity','Premium member tools']):
            with col: st.markdown(f'<div class="bm-trust"><div style="font-size:27px">{icon}</div><b>{title}</b><div class="bm-small">{sub}</div></div>',unsafe_allow_html=True)
        a,b=st.tabs(['🔐 LOGIN','✨ CREATE ACCOUNT'])
        with a:
            e=st.text_input('Email',key='login_email');p=st.text_input('Password',type='password',key='login_password')
            if st.button('🚀 ENTER BHARATMART',type='primary',key='login_btn',use_container_width=True):
                u=login(e,p)
                if u: st.session_state.user=u;st.rerun()
                else: st.error('Invalid email/password')
            st.info('Demo Admin: admin@bharatmart.com / BM_Admin_2026!\n\nDemo Customer: customer@bharatmart.com / BM_Customer_2026!')
        with b:
            n=st.text_input('Full Name',key='register_name');e2=st.text_input('Email',key='register_email');ph=st.text_input('Phone',key='register_phone');p2=st.text_input('Password',type='password',key='register_password');p3=st.text_input('Confirm Password',type='password',key='register_confirm')
            if st.button('✨ CREATE MY BHARATMART ACCOUNT',key='register_btn',use_container_width=True):
                if p2!=p3: st.error('Passwords do not match')
                elif len(p2)<6: st.error('Password must be at least 6 characters')
                else:
                    ok,msg=register(n,e2,ph,p2);(st.success if ok else st.error)(msg)
        st.markdown('<div class="bm-footer"><strong>BHARATMART MEGA MALL</strong><br>600 named products • 20 departments • Virtual shopping simulation</div>',unsafe_allow_html=True)
        return

    uid=st.session_state.user['id'];c=db();u=dict(c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone());adm=bool(c.execute('SELECT 1 FROM users WHERE id=? AND role="admin"',(uid,)).fetchone());unread=c.execute('SELECT COUNT(*) n FROM notifications WHERE user_id=? AND read=0',(uid,)).fetchone()['n'];c.close();st.session_state.user=u
    with st.sidebar:
        st.markdown(f'### 👋 Hi, {u["name"].split()[0]}')
        st.metric('💰 VIRTUAL WALLET',money(u['wallet']));st.metric('🏆 REWARD POINTS',f"{u['rewards']:,}")
        if u['vip']: st.markdown('<div class="bm-vip"><b>👑 BHARATMART PRIME</b><br><small>Exclusive virtual member</small></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="bm-benefit"><b>👑 Unlock Prime</b><br><small>Extra cashback • exclusive deals • priority simulation</small></div>',unsafe_allow_html=True)
            if st.button('ACTIVATE PRIME • ₹9,999',key='activate_vip',use_container_width=True):
                cc=db();ww=cc.execute('SELECT wallet FROM users WHERE id=?',(uid,)).fetchone()['wallet']
                if ww>=9999:
                    cc.execute('UPDATE users SET wallet=wallet-9999,vip=1 WHERE id=?',(uid,));cc.execute('INSERT INTO wallet_tx(user_id,amount,kind,created) VALUES(?,?,?,?)',(uid,-9999,'VIP MEMBERSHIP',now()));cc.commit();cc.close();notify(uid,'👑 Prime activated','Your BharatMart Prime membership is active.');st.success('Prime activated!');st.rerun()
                else: cc.close();st.error('Insufficient virtual wallet balance.')
        if st.button('🚪 LOGOUT',key='logout_btn',use_container_width=True):st.session_state.user=None;st.rerun()
        st.markdown('---')
        st.caption('100% VIRTUAL COMMERCE • No real payment is processed.')

    pages=['Home','Shop','AI Assistant','Cart','Orders','Wallet','Wishlist','Rewards','Reviews','Profile','Notifications']
    if adm: pages+=['ADMIN']
    page=st.radio('Navigation',pages,horizontal=True,key='main_navigation')

    if page=='Home':
        st.markdown('<div class="bm-hero"><span class="bm-chip">🇮🇳 INDIA\'S SMART VIRTUAL MALL</span><span class="bm-chip">⚡ FLASH SALE</span><span class="bm-chip">🤖 SMART RECOMMENDATIONS</span><span class="bm-chip">👑 PRIME</span><h1>Everything you need.<br>One BharatMart.</h1><p>Explore 20 departments and 600 named products with personalized discovery, smart cart savings, rewards, virtual checkout and transparent delivery tracking.</p></div>',unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns(4)
        c1.metric('🛍️ Named Products','600');c2.metric('🏪 Departments','20');c3.metric('⭐ Avg. Experience','4.7/5');c4.metric('🎁 Cashback','20–55%')
        st.markdown('<div class="bm-section">⚡ Flash Sale</div>',unsafe_allow_html=True)
        st.markdown('<div class="bm-flash"><h2>🔥 MEGA FLASH SALE</h2><div style="margin:5px 0 13px;color:#ffd9c8">Special virtual prices • limited-time style event</div><div class="bm-timer">02 : 14 : 37</div></div>',unsafe_allow_html=True)
        flash=product_rows(uid,8,sort='Popular');cols=st.columns(4)
        for i,x in enumerate(flash):
            with cols[i%4]:product_card(uid,x,i,'flash')
        st.markdown('<div class="bm-section">🛍️ Shop by Department</div>',unsafe_allow_html=True)
        cats=st.columns(5)
        for i,cat_name in enumerate(CATS):
            with cats[i%5]:
                st.markdown(f'<div class="bm-cat-tile"><div class="bm-cat-icon">{CATEGORY_ICONS.get(cat_name,"🛍️")}</div><div class="bm-cat">{cat_name}</div><div class="bm-small">30 named products</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="bm-section">📈 Trending Now</div>',unsafe_allow_html=True)
        trend=product_rows(uid,8,sort='Popular');tc=st.columns(4)
        for i,x in enumerate(trend):
            with tc[i%4]:product_card(uid,x,i,'trend')
        st.markdown('<div class="bm-section">🤖 Recommended for You</div><div class="bm-sub">Personalized from your shopping activity; new customers see popular products.</div>',unsafe_allow_html=True)
        rec=recommendations(uid,8);rc=st.columns(4)
        for i,x in enumerate(rec):
            with rc[i%4]:product_card(uid,x,i,'rec')
        st.markdown('<div class="bm-section">🏆 Why BharatMart?</div>',unsafe_allow_html=True)
        trust=st.columns(5)
        for col,ic,t,s in zip(trust,['🧠','💰','🚚','🛡️','🎯'],['Smart Shopping','Virtual ₹100Cr','5–7 Day Tracking','Transparent Demo','Rewards Engine'],['Recommendations','Starting balance','IST timeline','No real payment','Points & cashback']):
            with col:st.markdown(f'<div class="bm-trust"><div style="font-size:28px">{ic}</div><b>{t}</b><div class="bm-small">{s}</div></div>',unsafe_allow_html=True)

    elif page=='Shop':
        st.markdown('<div class="bm-section">🔎 Smart Product Discovery</div>',unsafe_allow_html=True)
        q=st.text_input('Search products, brands, categories or keywords',key='shop_search');cat=st.selectbox('Department',['All']+CATS,key='shop_category');sort=st.selectbox('Sort by',['Popular','Low Price','High Price','Rating','Newest'],key='shop_sort')
        ps=product_rows(uid,120,cat,q,sort);st.caption(f'{len(ps)} matching products • every listing has a unique name and product number')
        cols=st.columns(4)
        for i,x in enumerate(ps):
            with cols[i%4]:product_card(uid,x,i,'shop')

    elif page=='AI Assistant':
        st.markdown('<div class="bm-section">🤖 Ask Bharat — Smart Shopping Assistant</div>',unsafe_allow_html=True)
        st.markdown('<div class="bm-chat"><b>👋 Hello! I can help you discover products.</b><br><span class="bm-small">Try: “breakfast items under ₹500”, “show yogurt”, “best electronics”, or “fashion under ₹1500”.</span></div>',unsafe_allow_html=True)
        q=st.text_input('💬 What are you shopping for?',key='ai_query');budget=st.number_input('Optional maximum budget (₹)',min_value=0.0,value=0.0,step=100.0,key='ai_budget')
        if st.button('🤖 FIND PRODUCTS',type='primary',key='ai_find',use_container_width=True):
            rows,category=smart_answer(uid,q,budget if budget>0 else None);st.session_state['ai_rows']=rows;st.session_state['ai_category']=category
        rows=st.session_state.get('ai_rows',[])
        if rows:
            catmsg=st.session_state.get('ai_category');st.success(f'Bharat Assistant found {len(rows)} matches'+(f' in {catmsg}.' if catmsg else '.'))
            cols=st.columns(4)
            for i,x in enumerate(rows):
                with cols[i%4]:product_card(uid,x,i,'ai')
        else: st.info('Ask Bharat something above to start.')

    elif page=='Cart':
        rows=cart(uid)
        if not rows:st.info('🛒 Your cart is empty. Explore a department or ask Bharat AI for ideas.')
        else:
            st.markdown('<div class="bm-section">🛒 Your Smart Cart</div>',unsafe_allow_html=True)
            sub=sum(x['price']*x['qty'] for x in rows);discount=0
            for i,x in enumerate(rows):
                a,b,c3=st.columns([1,5,1]);a.image(product_image(x['name'],''),width=75);b.markdown(f'**{x["name"]}**  \n<span class="bm-small">Product #{x["product_id"]} • {x["qty"]} × {money(x["price"])}</span>',unsafe_allow_html=True);c3.write(money(x['price']*x['qty']))
                if st.button('Remove',key=f'cart_remove_{x["product_id"]}_{i}'):remove(uid,x['product_id']);st.rerun()
            coupon=st.text_input('🏷️ Coupon code: WELCOME10 / FESTIVE20 / MEGASALE50',key='cart_coupon')
            if coupon.upper()=='WELCOME10' and sub>=500:discount=min(sub*.10,300)
            elif coupon.upper()=='FESTIVE20' and sub>=1500:discount=min(sub*.20,500)
            elif coupon.upper()=='MEGASALE50' and sub>=5000:discount=min(sub*.50,25000)
            fee=0 if sub-discount>=500 else 49;total=round(sub-discount+fee,2);benefit=round(discount+max(0,sub*.05),2)
            st.markdown(f'<div class="bm-benefit"><b>🧠 SMART CART SCORE</b><div class="bm-score">{min(99,int(72+len(rows)*4))}/100</div><div>Estimated customer benefit: <b>{money(benefit)}</b> • cashback after delivery included</div></div>',unsafe_allow_html=True)
            st.markdown('#### ① Delivery Address')
            addresses=get_addresses(uid);labels=['+ Add a new virtual address']+[f'{a["label"]} — {a["city"]}, {a["pincode"]}' for a in addresses];sel=st.selectbox('Choose address',labels,key='cart_address')
            if sel==labels[0]:
                aa,bb=st.columns(2);label=aa.text_input('Label',value='Home',key='addr_label');phone=bb.text_input('Phone',key='addr_phone');address=st.text_input('Full address',key='addr_text');city=st.text_input('City',key='addr_city');state=st.text_input('State',value='West Bengal',key='addr_state');pin=st.text_input('PIN code',key='addr_pin')
                if st.button('SAVE ADDRESS',key='save_address'):save_address(uid,label,address,city,state,pin,phone);st.success('Address saved');st.rerun()
            st.markdown('#### ② Payment')
            method=st.selectbox('Payment method',['Virtual Wallet','Simulated Online Payment','Cash on Delivery (Virtual)'],key='cart_payment')
            st.markdown(f'<div class="bm-benefit"><b>Subtotal</b> {money(sub)} &nbsp; • &nbsp; <b>Discount</b> -{money(discount)} &nbsp; • &nbsp; <b>Delivery</b> {"FREE" if fee==0 else money(fee)}<br><hr><span style="font-size:22px;font-weight:900">Total {money(total)}</span></div>',unsafe_allow_html=True)
            st.markdown('#### ③ Confirm')
            st.progress(0.9)
            if st.button('🚀 PLACE ORDER & START TRACKING',type='primary',use_container_width=True,key='place_order_btn'):
                if sel==labels[0] and not addresses:st.error('Please save a delivery address first.')
                else:
                    oid,err=place(uid,method,coupon)
                    if err:st.error(err)
                    else:add_reward(uid,50,'Placed an order');notify(uid,'📦 Order placed',f'Order #{oid} is now in tracking.');st.success(f'Order #{oid} placed!');st.balloons();st.rerun()

    elif page=='Orders':
        c=db();os_=c.execute('SELECT * FROM orders WHERE user_id=? ORDER BY id DESC',(uid,)).fetchall();c.close()
        if not os_:st.info('No orders yet. Your orders will appear here with live-style tracking.')
        for oi,o0 in enumerate(os_):
            sync(o0['id']);c=db();o=c.execute('SELECT * FROM orders WHERE id=?',(o0['id'],)).fetchone();items=c.execute('SELECT oi.*,p.name,p.category FROM order_items oi JOIN products p ON p.id=oi.product_id WHERE oi.order_id=?',(o['id'],)).fetchall();c.close()
            idx=STEPS.index(o['status']) if o['status'] in STEPS else 0; pct=idx/4
            with st.expander(f'📦 ORDER #{o["id"]} • {money(o["total"])} • {o["status"]}',expanded=(oi==0)):
                st.progress(pct);st.markdown(f'<div class="bm-track"><b>Tracking ID:</b> {o["tracking"]}<br><span class="bm-small">Ordered {fmt_ist(o["created"])} • Expected {fmt_ist(o["expected_delivery"])}</span></div>',unsafe_allow_html=True)
                schedule=[('ORDER PLACED',o['created']),('CAME TO STORE',o['came_to_store_at']),('PACKED',o['packed_at']),('OUT FOR DELIVERY',o['out_for_delivery_at']),('DELIVERED',o['expected_delivery'])]
                cols=st.columns(5)
                for j,(label,when) in enumerate(schedule):
                    with cols[j]:st.markdown(f'<div class="bm-trust"><div style="font-size:21px">{"✅" if j<=idx else "○"}</div><b>{label}</b><div class="bm-small">{fmt_ist(when) if when else "Pending"}</div></div>',unsafe_allow_html=True)
                st.write(f'🎁 Cashback: **{o["cb_pct"]:.0f}% = {money(o["cb_amt"])}**')
                for x in items:st.write(f'• {x["name"]} × {x["qty"]} — {money(x["price"]*x["qty"])}')
                if o['status']!='DELIVERED' and st.button('⏭️ SIMULATE NEXT STAGE',key=f'order_next_{o["id"]}'):force_next(o['id']);st.rerun()

    elif page=='Wallet':
        c=db();w=c.execute('SELECT wallet,rewards FROM users WHERE id=?',(uid,)).fetchone();tx=c.execute('SELECT * FROM wallet_tx WHERE user_id=? ORDER BY id DESC LIMIT 50',(uid,)).fetchall();c.close()
        st.markdown(f'<div class="bm-wallet"><div style="font-size:12px;letter-spacing:2px">💳 BHARATMART WALLET</div><div class="bm-wallet-value">{money(w["wallet"])}</div><div>Available virtual balance • No real money</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="bm-section">💰 Wallet Intelligence</div>',unsafe_allow_html=True);a,b,c3=st.columns(3);a.metric('Available',money(w['wallet']));b.metric('Rewards',f'{w["rewards"]:,}');c3.metric('VIP', 'ACTIVE' if u['vip'] else 'NOT ACTIVE')
        st.markdown('### Transaction History');st.dataframe([dict(x) for x in tx],use_container_width=True)

    elif page=='Wishlist':
        c=db();ws=c.execute('SELECT p.* FROM wishlist w JOIN products p ON p.id=w.product_id WHERE w.user_id=?',(uid,)).fetchall();c.close();st.markdown('<div class="bm-section">♡ Saved for Later</div>',unsafe_allow_html=True)
        if not ws:st.info('Your wishlist is empty.')
        cols=st.columns(4)
        for i,x in enumerate(ws):
            with cols[i%4]:product_card(uid,x,i,'wishlist')

    elif page=='Rewards':
        c=db();events=c.execute('SELECT * FROM reward_events WHERE user_id=? ORDER BY id DESC LIMIT 30',(uid,)).fetchall();c.close();pts=u['rewards'];level='Bronze' if pts<500 else 'Silver' if pts<1500 else 'Gold' if pts<3000 else 'Platinum' if pts<6000 else 'Maharaja';nextp=500 if pts<500 else 1500 if pts<1500 else 3000 if pts<3000 else 6000 if pts<6000 else pts+2000;progress=min(1,pts/nextp)
        st.markdown('<div class="bm-section">🏆 BharatMart Rewards</div>',unsafe_allow_html=True);st.markdown(f'<div class="bm-benefit"><div class="bm-score">{level}</div><b>{pts:,} points</b><div class="bm-small">Next milestone: {nextp:,} points</div></div>',unsafe_allow_html=True);st.progress(progress)
        r1,r2,r3,r4=st.columns(4);r1.metric('🛒 Cart add','+2');r2.metric('♡ Wishlist','+1');r3.metric('📦 Order','+50');r4.metric('⭐ Review','+25')
        st.markdown('### Recent reward activity');st.dataframe([dict(x) for x in events],use_container_width=True)

    elif page=='Reviews':
        st.markdown('<div class="bm-section">⭐ Reviews & Ratings</div>',unsafe_allow_html=True);cc=db();products=cc.execute('SELECT * FROM products ORDER BY sold DESC LIMIT 120').fetchall();cc.close();chosen=st.selectbox('Choose a product',products,format_func=lambda z:f'#{z["id"]} • {z["name"]} • {money(z["price"])}',key='review_product');rating=st.slider('Your rating',1,5,5,key='review_rating');review_text=st.text_area('Write your review',max_chars=500,key='review_text')
        if st.button('⭐ SUBMIT REVIEW',key='submit_review',type='primary'):
            if not review_text.strip():st.error('Please write a review.')
            else:
                cc=db();cc.execute('INSERT INTO reviews(user_id,product_id,rating,review,created) VALUES(?,?,?,?,?) ON CONFLICT(user_id,product_id) DO UPDATE SET rating=excluded.rating,review=excluded.review,created=excluded.created',(uid,chosen['id'],rating,review_text.strip(),now()));avg=cc.execute('SELECT AVG(rating) a FROM reviews WHERE product_id=?',(chosen['id'],)).fetchone()['a'];cc.execute('UPDATE products SET rating=? WHERE id=?',(round(avg or 0,1),chosen['id']));cc.commit();cc.close();add_reward(uid,25,'Submitted product review');notify(uid,'⭐ Review reward','You earned 25 reward points for your review.');st.success('Review saved and points added.');st.rerun()
        cc=db();rv=cc.execute('SELECT r.*,u.name FROM reviews r JOIN users u ON u.id=r.user_id WHERE r.product_id=? ORDER BY r.id DESC LIMIT 30',(chosen['id'],)).fetchall();cc.close();
        st.markdown(f'### ⭐ {chosen["rating"]:.1f} / 5 • {chosen["name"]}')
        for i,r in enumerate(rv):st.markdown(f'<div class="bm-benefit"><b>👤 {r["name"]}</b> • ⭐ {r["rating"]}/5<br>{r["review"]}<br><span class="bm-small">{fmt_ist(r["created"])}</span></div>',unsafe_allow_html=True)

    elif page=='Profile':
        st.markdown('<div class="bm-section">👤 My BharatMart Profile</div>',unsafe_allow_html=True);a,b,c3=st.columns(3);a.metric('Name',u['name']);b.metric('VIP','ACTIVE' if u['vip'] else 'STANDARD');c3.metric('Rewards',f'{u["rewards"]:,}')
        st.write(f'**Email:** {u["email"]}');st.write(f'**Phone:** {u["phone"] or "Not added"}')
        st.markdown('### 🏪 Marketplace identity');st.info('BharatMart connects virtual departments and virtual sellers: BharatFresh, Bharat Electronics, Bharat Fashion, Bharat Home, Bharat Sports and more.')
        st.markdown('### 👑 Prime benefits');st.write('Priority simulation • extra cashback • exclusive virtual deals • early event access')

    elif page=='Notifications':
        c=db();ns=c.execute('SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 40',(uid,)).fetchall();c.execute('UPDATE notifications SET read=1 WHERE user_id=?',(uid,));c.commit();c.close();st.markdown('<div class="bm-section">🔔 Notifications</div>',unsafe_allow_html=True)
        if not ns:st.info('No notifications yet.')
        for n in ns:st.markdown(f'<div class="bm-benefit"><b>{n["title"]}</b><br>{n["body"]}<br><span class="bm-small">{fmt_ist(n["created"])}</span></div>',unsafe_allow_html=True)

    elif page=='ADMIN':
        st.markdown('<div class="bm-section">👨‍💼 BharatMart Business Intelligence</div>',unsafe_allow_html=True)
        c=db();stats=[c.execute('SELECT COUNT(*) n FROM products').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM users WHERE role="customer"').fetchone()['n'],c.execute('SELECT COUNT(*) n FROM orders').fetchone()['n'],c.execute('SELECT COALESCE(SUM(total),0) n FROM orders').fetchone()['n']];low=c.execute('SELECT name,category,stock FROM products WHERE stock<=10 ORDER BY stock ASC LIMIT 20').fetchall();orders=c.execute('SELECT o.*,u.name,u.email FROM orders o JOIN users u ON u.id=o.user_id ORDER BY o.id DESC').fetchall();cat_sales=c.execute('SELECT category,SUM(sold) sold FROM products GROUP BY category ORDER BY sold DESC').fetchall();c.close()
        a,b,c3,d=st.columns(4);a.metric('Products',stats[0]);b.metric('Customers',stats[1]);c3.metric('Orders',stats[2]);d.metric('Virtual Sales',money(stats[3]))
        st.markdown('### 📈 Sales & Department Intelligence');st.bar_chart({x['category']:x['sold'] for x in cat_sales})
        st.markdown('### ⚠️ Inventory Intelligence');st.dataframe([dict(x) for x in low],use_container_width=True)
        st.markdown('### 🏪 Virtual Marketplace Sellers');st.write('BharatFresh • Bharat Electronics • Bharat Fashion • Bharat Home • Bharat Sports • Bharat Beauty • Bharat Luxe • Bharat Care • Bharat Gaming')
        st.markdown('### 📦 Order Control')
        for o in orders:
            sync(o['id']);st.write(f'**#{o["id"]} {o["name"]}** — {money(o["total"])} — {o["status"]} — Cashback {money(o["cb_amt"])}')
            if o['status']!='DELIVERED' and st.button('Advance',key=f'admin_advance_{o["id"]}'):force_next(o['id']);st.rerun()

    st.markdown('<div class="bm-footer"><strong>BHARATMART MEGA MALL</strong><br>India\'s smart virtual marketplace • 20 departments • 600 named products • AI-style discovery • Prime • Rewards • Flash Sales • Smart Cart • IST tracking<br><span class="bm-small">Demo/simulation only — no real payments, real delivery or real financial transfers.</span></div>',unsafe_allow_html=True)

if __name__=='__main__':main()
