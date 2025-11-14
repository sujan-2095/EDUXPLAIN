# PostgreSQL Setup Guide for Render

This application has been configured to use PostgreSQL on Render's free tier, with automatic fallback to SQLite for local development.

## ✅ What's Been Done

1. ✅ Added `flask-sqlalchemy` and `psycopg2-binary` to `requirements.txt`
2. ✅ Created database models using SQLAlchemy
3. ✅ Converted all database operations from SQLite to SQLAlchemy
4. ✅ Configured automatic database URL detection (PostgreSQL on Render, SQLite locally)

## 🚀 Setup Steps for Render

### Step 1: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Select **Free Tier**
4. Give it a name (e.g., `eduxplain-db`)
5. Click **Create Database**
6. Wait for it to be created

### Step 2: Copy Database URL

1. Once created, click on your database
2. Find the **Internal Database URL** or **External Database URL**
3. Copy the URL (looks like: `postgresql://user:password@host:port/dbname`)

### Step 3: Add Environment Variable to Your Web Service

1. Go to your Flask web service on Render
2. Click on **Environment**
3. Add a new environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the database URL you copied
4. Click **Save Changes**

### Step 4: Deploy

The application will automatically:
- ✅ Detect the `DATABASE_URL` environment variable
- ✅ Connect to PostgreSQL
- ✅ Create all necessary tables on first run
- ✅ Store all data persistently

## 🧪 Local Development

For local development, the app automatically uses SQLite (no setup needed):
- If `DATABASE_URL` is not set, it uses `data/eduxplain.db`
- All features work the same way

## 📝 Database Models

The application uses two main tables:

1. **users** - Stores user accounts (username, email, password_hash)
2. **predictions** - Stores student predictions with user associations

Tables are automatically created on first run using `db.create_all()`.

## 🔍 Verification

After deployment, check your Render logs to ensure:
- Database connection is successful
- Tables are created
- No errors related to database operations

## 💡 Benefits

- ✅ **Free** - Uses Render's free PostgreSQL tier
- ✅ **Persistent** - Data never gets deleted
- ✅ **Scalable** - Can upgrade to paid tier if needed
- ✅ **Compatible** - Works with all Flask features
- ✅ **No disk needed** - Database is managed by Render

