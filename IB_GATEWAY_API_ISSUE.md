# 🔌 IB Gateway API Setup - Simple Guide

## ❌ Current Issue
Your IB Gateway is **logged in via web browser** (not the desktop app), which doesn't support TWS API connections.

## ✅ Solution: Use Desktop IB Gateway

You have TWO options:

---

## **Option 1: Easiest - Use Client Portal API (Web-Based)**

Since you're using IB Gateway through the browser, switch to the **Client Portal Web API**:

### Update Rick's Connector:
This requires a different approach - the Client Portal API uses REST/WebSocket instead of TWS socket.

**Pros**: No desktop app needed, works with your current browser login
**Cons**: Different API, would need to modify `ib_connector.py`

---

## **Option 2: Recommended - Install Desktop IB Gateway**

### Step 1: Close browser IB Gateway

### Step 2: Download Desktop Version
Go to: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
- Click "IB Gateway Standalone (Linux)"
- Download: `ibgateway-stable-standalone-linux-x64.sh`

### Step 3: Install
```bash
cd ~/Downloads  # or wherever you downloaded
chmod +x ibgateway-stable-standalone-linux-x64.sh
./ibgateway-stable-standalone-linux-x64.sh
```

### Step 4: Launch Desktop Gateway
```bash
~/Jts/ibgateway/*/ibgateway
```

### Step 5: Login
- Enter your IB credentials
- **Important**: Choose **Paper Trading**

### Step 6: Enable API
After login, in the IB Gateway desktop app:
- Go to: **Configure → Settings → API → Settings**
- Check: **Enable ActiveX and Socket Clients**
- Socket Port: **4002**
- Check: **Allow connections from localhost only**
- Click **OK**

### Step 7: Test Connection
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
python3 check_ib_balance.py
```

---

## 🎯 Why Desktop Gateway?

| Feature | Browser Gateway | Desktop Gateway |
|---------|----------------|-----------------|
| TWS API Support | ❌ No | ✅ Yes |
| Socket Connection | ❌ No | ✅ Port 4002 |
| Rick Compatible | ❌ No | ✅ Yes |
| `ib_insync` Works | ❌ No | ✅ Yes |

---

## 📋 Summary

**Current Setup**: Browser-based IB Gateway (no TWS API socket)  
**What Rick Needs**: Desktop IB Gateway with TWS API enabled  
**Solution**: Install desktop version OR switch to Client Portal API

**Recommendation**: Install desktop IB Gateway - it's a one-time 5-minute setup and then Rick can connect automatically.

---

## 🚀 Quick Start (Desktop Gateway)

```bash
# 1. Download installer
wget https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh

# 2. Install
chmod +x ibgateway-stable-standalone-linux-x64.sh
./ibgateway-stable-standalone-linux-x64.sh

# 3. Run
~/Jts/ibgateway/*/ibgateway

# 4. Enable API in GUI settings

# 5. Test
cd /home/ing/RICK/RICK_LIVE_CLEAN
python3 check_ib_balance.py
```

**That's it!** Once desktop Gateway is running with API enabled, Rick connects automatically.
