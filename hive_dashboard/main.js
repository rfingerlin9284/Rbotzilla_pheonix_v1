const { app, BrowserWindow, Menu } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const express = require('express')
const http = require('http')
const WebSocket = require('ws')

let mainWindow
let webServer
let wsServer

// Web server for dashboard
function createWebServer() {
  const webApp = express()
  
  // Serve static files
  webApp.use(express.static(path.join(__dirname, 'public')))
  
  // Main dashboard route
  webApp.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'))
  })
  
  // API endpoints
  webApp.get('/api/status', (req, res) => {
    res.json({
      status: 'operational',
      timestamp: new Date().toISOString(),
      system: 'RBOTzilla UNI',
      version: '1.0.0'
    })
  })
  
  webServer = http.createServer(webApp)
  
  // WebSocket server for live terminal
  wsServer = new WebSocket.Server({ server: webServer })
  
  wsServer.on('connection', (ws) => {
    console.log('Client connected to terminal stream')
    
    ws.on('message', (message) => {
      const data = JSON.parse(message)
      if (data.type === 'command') {
        // Handle terminal commands
        console.log('Terminal command:', data.command)
        ws.send(JSON.stringify({
          type: 'output',
          data: `Executing: ${data.command}\n`
        }))
      }
    })
    
    ws.on('close', () => {
      console.log('Client disconnected from terminal stream')
    })
  })
  
  webServer.listen(3000, () => {
    console.log('RBOTzilla web server running on http://localhost:3000')
  })
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false // Allow localhost connections
    },
    icon: path.join(__dirname, 'assets/icon.png'),
    titleBarStyle: 'default',
    frame: true,
    show: false // Hide until ready
  })

  // Load the dashboard
  mainWindow.loadURL('http://localhost:3000')

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    
    // Focus window
    if (process.platform === 'darwin') {
      app.dock.show()
    }
    mainWindow.focus()
  })

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // Development mode - open DevTools
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools()
  }
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'RBOTzilla',
      submenu: [
        {
          label: 'About RBOTzilla UNI',
          click: () => {
            // Show about dialog
          }
        },
        { type: 'separator' },
        {
          label: 'System Status',
          click: () => {
            mainWindow.webContents.send('show-status')
          }
        },
        {
          label: 'Trading Console',
          click: () => {
            mainWindow.webContents.send('show-console')
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit()
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

// App event handlers
app.whenReady().then(() => {
  // Start web server first
  createWebServer()
  
  // Give server time to start
  setTimeout(() => {
    createWindow()
    createMenu()
  }, 1000)

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (webServer) {
    webServer.close()
  }
  
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  if (webServer) {
    webServer.close()
  }
})

// Handle certificate errors (for development)
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  event.preventDefault()
  callback(true)
})