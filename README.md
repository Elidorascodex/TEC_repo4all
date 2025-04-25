# TEC_repo4all

The central automation & AI agent infrastructure for the Elidoras Codex project. This repo houses all intelligent systems that power TEC — from crypto wallet trackers to ClickUp task transformers and WordPress automation bots.

## ✨ Purpose

To build, deploy, and maintain recursive AI agents that:
- Automate content across ClickUp & WordPress
- Power $TECTrace crypto logic
- Process sentiment, trigger lore drops
- Operate across ETH, XRP, ADA chains
- Serve the TEC factions through intelligent automation

## 🤖 Bots Included

- `TECTraceBot`: Crypto scanner & analyzer
- `ClickUpAgent`: Task sorter, auto-writer
- `WordPressHandler`: Posts summaries to elidorascodex.com
- `Airth/Trace`: Persona-layered AIs for lore interaction & automation

## 🔐 Setup

### Automation Agents

```bash
# Ensure you have Python 3.8+ installed
# Clone the repository (if you haven't already)
# git clone <repository-url>
# cd TEC_repo4all

# Create a virtual environment (recommended)
python -m venv venv
# Activate the virtual environment
# On Windows: .\venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Copy the example environment file and fill in your API keys/secrets
cp config/.env.example config/.env 
# (Edit config/.env with your details)

# Install required Python packages
pip install -r requirements.txt

# Run the main automation script (example)
python scripts/run_automation.py 
```

### WordPress Theme (tec-theme)

To use the custom `tec-theme` on your WordPress site:

1.  **Package the Theme:** Create a zip archive of the `wordpress/tec-theme` directory. Make sure the `style.css` and `index.php` files are at the root level within the zip file, not inside a nested `tec-theme` folder.
    *   Example: Select all files/folders inside `wordpress/tec-theme` and zip them directly into `tec-theme.zip`.
2.  **Upload to WordPress:**
    *   Log in to your WordPress Admin dashboard.
    *   Navigate to `Appearance` -> `Themes`.
    *   Click the `Add New` button at the top.
    *   Click the `Upload Theme` button.
    *   Choose the `tec-theme.zip` file you created and click `Install Now`.
3.  **Activate the Theme:** Once the theme is installed, click the `Activate` button.
4.  **Configure:**
    *   Set up the necessary menus under `Appearance` -> `Menus` (Primary, Footer, Factions).
    *   Configure any required widgets under `Appearance` -> `Widgets`.
    *   Ensure any necessary plugins (if the theme depends on them) are installed and activated.
    *   Review theme options (if available in the Customizer under `Appearance` -> `Customize`).

## 🧠 License

MIT — you may fork, remix, and re-deploy.

## 🪙 $TEC & $TECRP

Dual-chain logic enabled. Supports ERC-20 & XRPL token integrations.

---

This repo is a digital temple.
Do not just deploy. **Invoke.**

