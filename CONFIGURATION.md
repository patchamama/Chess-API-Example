# Configuration Guide

## Backend URL Configuration

The chess application frontend can connect to different backend servers using a configuration file.

## Quick Start

1. Copy the example configuration:
   ```bash
   cp config.json.example config.json
   ```

2. The default configuration works for local development:
   ```json
   {
     "backend_url": "http://127.0.0.1:5000"
   }
   ```

3. No further changes needed if running locally!

## Configuration Options

### Local Development (Default)
```json
{
  "backend_url": "http://127.0.0.1:5000"
}
```
Use this when running the backend on your local machine.

### Different Port
```json
{
  "backend_url": "http://127.0.0.1:8080"
}
```
If your backend runs on a different port.

### Local Network Access
```json
{
  "backend_url": "http://192.168.1.100:5000"
}
```
Use this to connect to a backend on another computer in your local network.
Replace `192.168.1.100` with the actual IP address of the backend server.

### Production Server
```json
{
  "backend_url": "https://chess-backend.example.com"
}
```
Use this when deploying to a production environment.

## How It Works

1. When the page loads, it tries to fetch `config.json`
2. If found, it reads the `backend_url` value
3. If not found, it uses the default: `http://127.0.0.1:5000`
4. All API calls use this URL

## No Configuration File?

If you don't create a `config.json` file, the application will automatically use:
```
http://127.0.0.1:5000
```

This is perfect for quick local development!

## Verification

Open the browser console (F12) and look for one of these messages:

Success with config file:
```
Loaded backend URL from config.json: http://127.0.0.1:5000
```

Using default:
```
No config.json found, using default backend URL: http://127.0.0.1:5000
```

## Troubleshooting

### Config file not loading

Make sure:
1. File is named exactly `config.json` (not `config.json.txt`)
2. File is in the same directory as `advanced_chess.html`
3. JSON syntax is valid (use a JSON validator)
4. You're running through a web server (not opening the file directly)

### Invalid JSON error

Validate your JSON at https://jsonlint.com/

Common mistakes:
- Missing quotes around strings
- Trailing commas
- Single quotes instead of double quotes

### Still using wrong URL

1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check browser console for error messages

## Git and Version Control

The `.gitignore` file is configured to ignore `config.json`, so your personal configuration won't be committed to version control. 

Always commit `config.json.example` so other developers know what to configure.

## Advanced: Multiple Environments

You can have different config files for different environments:

```bash
# Development
cp config.json.example config.json
# Edit for local development

# Production
cp config.json.example config.production.json
# Edit for production

# Use symbolic links to switch
ln -sf config.production.json config.json
```

## Security Note

Never commit real production URLs with sensitive information to version control. Always use:
- `config.json.example` for examples (committed)
- `config.json` for real configuration (not committed)
