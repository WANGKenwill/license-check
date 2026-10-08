import {spawn} from 'node:child_process';
export function encode(){return spawn('ffmpeg',['-i','input.mov','output.mp4']);}
