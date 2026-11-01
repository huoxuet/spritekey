"""Self-contained local-file viewer, with all frame data in the document."""
import base64
import json

def write_preview(path, files, durations):
    frames = ["data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii") for p in files]
    times = [float(x)*1000 if x is not None else None for x in durations]
    payload = json.dumps({"frames":frames, "durations":times}, separators=(",", ":"))
    html = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>SpriteKey local preview</title><style>
body{font:16px system-ui;margin:24px;background:#eee;color:#222}button,input{margin:6px}#stage{display:inline-block;background:#fff;border:1px solid #888}img{display:block;max-width:90vw;image-rendering:auto}#stage.dark{background:#222}#stage.check{background:conic-gradient(#ccc 25%,#fff 0 50%,#ccc 0 75%,#fff 0) 0 0/20px 20px}
</style><h1>SpriteKey local preview</h1><p id="status"></p>
<button id="play">Play</button><button id="prev">Previous</button><button id="next">Next</button>
<button id="light">Light</button><button id="dark">Dark</button><button id="check">Checker</button>
<input id="seek" type="range" min="0" value="0"><br><div id="stage" class="check"><img id="image" alt="Extracted frame"></div>
<script>const data=PAYLOAD;let i=0,playing=false,timer;
const image=document.getElementById('image'),seek=document.getElementById('seek'),status=document.getElementById('status');seek.max=data.frames.length-1;
function draw(){image.src=data.frames[i];seek.value=i;status.textContent=`Frame ${i+1} / ${data.frames.length}`+(data.durations[i]===null?' — timing UNKNOWN; playback disabled':` — ${data.durations[i]} ms`)}
function stop(){playing=false;clearTimeout(timer);document.getElementById('play').textContent='Play'}
function tick(){if(!playing)return;draw();timer=setTimeout(()=>{i=(i+1)%data.frames.length;tick()},data.durations[i])}
document.getElementById('play').disabled=data.durations.some(x=>x===null);
document.getElementById('play').onclick=()=>{if(playing)stop();else{playing=true;document.getElementById('play').textContent='Pause';tick()}};
document.getElementById('prev').onclick=()=>{stop();i=(i+data.frames.length-1)%data.frames.length;draw()};
document.getElementById('next').onclick=()=>{stop();i=(i+1)%data.frames.length;draw()};seek.oninput=()=>{stop();i=Number(seek.value);draw()};
for(const name of ['light','dark','check'])document.getElementById(name).onclick=()=>document.getElementById('stage').className=name;
draw();</script></html>'''
    path.write_text(html.replace("PAYLOAD", payload), encoding="utf-8")
