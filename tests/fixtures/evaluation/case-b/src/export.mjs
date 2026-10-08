import {spawn} from 'node:child_process';
export function encode(){return spawn('ffmpeg',['-f','rawvideo','-i','pipe:0','output.mp4']);}
