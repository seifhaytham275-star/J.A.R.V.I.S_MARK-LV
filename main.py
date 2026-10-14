<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Mark LV Improved UI</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            display: flex;
            height: 100vh;
        }

        #sidebar {
            width: 280px;
            background-color: #1e1e1e;
            padding: 20px;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #333;
        }

        h1 {
            font-size: 1.5rem;
            color: #00bcd4;
            margin-bottom: 30px;
            text-align: center;
        }

        .config-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-size: 0.9rem;
            color: #aaa;
        }

        select, input[type="text"] {
            width: 100%;
            padding: 10px;
            background-color: #2a2a2a;
            border: 1px solid #444;
            color: #fff;
            border-radius: 5px;
            box-sizing: border-box; 
        }

        button {
            padding: 10px;
            background-color: #00838f;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #00acc1;
        }

        #main-content {
            flex-grow: 1;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        #chat-area {
            width: 100%;
            max-width: 800px;
            flex-grow: 1;
            background-color: #1e1e1e;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            overflow-y: auto;
            border: 1px solid #333;
        }

        #input-group {
            width: 100%;
            max-width: 800px;
            display: flex;
            gap: 10px;
        }

        #message-input {
            flex-grow: 1;
        }

        #upload-btn {
            background-color: #424242;
        }
    </style>
</head>
<body>
    <div id="sidebar">
        <h1>J.A.R.V.I.S. LV</h1>
        
        <div class="config-group">
            <label>Response Language</label>
            <select>
                <option>English</option>
                <option>Arabic</option>
            </select>
        </div>

        <div class="config-group">
            <label>Voice Tone</label>
            <select>
                <option>Puck</option>
                <option>Cassandra</option>
            </select>
        </div>

        <div class="config-group">
            <label>API Key</label>
            <input type="text" placeholder="Enter key...">
        </div>

        <button style="margin-top: auto;">Clear Conversation</button>
    </div>

    <div id="main-content">
        <div id="chat-area">
            <!-- Messages appear here -->
        </div>

        <div id="input-group">
            <button id="upload-btn">+</button>
            <input type="text" id="message-input" placeholder="Message JARVIS...">
            <button>Send</button>
        </div>
    </div>
</body>
</html>
