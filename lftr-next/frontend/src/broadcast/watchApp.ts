import '../styles/broadcast.css';
import { BroadcastChat } from './chat';
import { JsonSocket } from './signaling';
import { bindUploadPlaceholder } from './uploads';
import { bindWebSearchPlaceholder } from './webSearchPane';

const root = document.querySelector<HTMLElement>('#broadcast-app') ?? document.body;
root.innerHTML = `<main class="broadcast-shell"><section class="stage"><header><h1>LFTR Watch</h1></header><video id="viewer" playsinline muted controls></video><footer><button id="play">Start Muted Playback</button><button id="toggle-chat">Toggle Chat</button></footer></section><aside class="panel"><header><h2>Viewer Chat</h2></header><div class="status" id="status">booting</div><div class="hooks"><button id="upload">Image hook</button> <button id="search">Search hook</button></div><div class="chat-log" id="chat"></div><form class="chat-form" id="form"><input id="text" placeholder="Message" autocomplete="off"><button>Send</button></form><div class="debug" id="debug">No GFS renderer loaded.</div></aside></main>`;
const status = (line: string) => { document.querySelector('#status')!.textContent = line; };
const debug = (line: string) => { document.querySelector('#debug')!.textContent = line; };
const room = new URLSearchParams(location.search).get('room') ?? 'default';
const signal = new JsonSocket('/ws/watch', (msg) => debug(`${msg.family ?? 'signal'}:${msg.type}`), status); signal.connect(room);
const chat = new BroadcastChat(document.querySelector<HTMLElement>('#chat')!, status); chat.connect(room);
document.querySelector<HTMLButtonElement>('#play')!.onclick = () => { const video = document.querySelector<HTMLVideoElement>('#viewer')!; video.muted = true; video.play().then(() => status('muted playback requested')).catch((error) => status(`playback needs user gesture: ${error.message}`)); };
document.querySelector<HTMLButtonElement>('#toggle-chat')!.onclick = () => document.querySelector('.broadcast-shell')!.classList.toggle('collapsed');
bindUploadPlaceholder(document.querySelector<HTMLButtonElement>('#upload')!, status, () => chat.sendUploadPlaceholder());
bindWebSearchPlaceholder(document.querySelector<HTMLButtonElement>('#search')!, status);
document.querySelector<HTMLFormElement>('#form')!.onsubmit = (event) => { event.preventDefault(); const input = document.querySelector<HTMLInputElement>('#text')!; chat.send(input.value, 'Viewer'); input.value = ''; };
