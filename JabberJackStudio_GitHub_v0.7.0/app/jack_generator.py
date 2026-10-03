import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import subprocess, shutil, tempfile, wave, math, os, sys
import numpy as np
from PIL import Image, ImageTk

APP_DIR=Path(__file__).resolve().parent
ROOT_DIR=Path(sys.executable).resolve().parent if getattr(sys,"frozen",False) else APP_DIR.parent
ASSETS=ROOT_DIR/"assets"; FACES=ASSETS/"faces"; TOOLS=ROOT_DIR/"tools"; OUTPUT=ROOT_DIR/"output"
OUTPUT.mkdir(exist_ok=True)
FACE_NAMES=["Traditional","Funny","Scary","Angry"]
NATIVE_W,NATIVE_H,FPS=208,176,16
FACTORY=["01_trad_VO_2E.amv","02_Audio Adjusted Traditional Pumpkin Singing_1.amv","03_Traditional Pumpkin Emotions.amv","04_Angry_VO_2E.amv","05_Audio Adjusted Scary Pumpkin Singing_1.amv","06_Scary Pumpkin Emotions.amv","07_0Funny_VO_2E.amv","08_Audio Adjusted Stupid Pumpkin Singing_1.amv","09_Stupid Pumpkin Emotions.amv","10_StillFaces.amv","Custom (11+)"]

def find_ffmpeg():
    p=TOOLS/"ffmpeg.exe"
    return str(p) if p.exists() else shutil.which("ffmpeg")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JabberJack Studio v0.7.0"); self.geometry("980x860"); self.minsize(900,760)
        self.ffmpeg=find_ffmpeg(); self.status=tk.StringVar(value="Ready")
        self.audio=tk.StringVar(); self.video=tk.StringVar(); self.face=tk.StringVar(value="Scary")
        self.rotate=tk.BooleanVar(value=False); self.pause=tk.IntVar(value=5); self.pause_mode=tk.StringVar(value="Idle + Expressions")
        self.slot=tk.StringVar(value="Custom (11+)"); self.name=tk.StringVar(value="11_Custom.amv")
        self.fit=tk.StringVar(value="Crop to Fill"); self.keep_audio=tk.BooleanVar(value=True)
        self.trim_start=tk.StringVar(value="0"); self.trim_end=tk.StringVar(value="")
        self.video_pause_mode=tk.StringVar(value="Black")
        self.images={}
        self.build()

    def build(self):
        top=ttk.Frame(self,padding=14); top.pack(fill="both",expand=True)
        ttk.Label(top,text="JabberJack Studio",font=("Segoe UI",22,"bold")).pack(anchor="w")
        ttk.Label(top,text="Create talking pumpkin animations or convert your own videos for Jabberin' Jack.").pack(anchor="w",pady=(0,10))
        nb=ttk.Notebook(top); nb.pack(fill="both",expand=True)
        talk=ttk.Frame(nb,padding=12); vid=ttk.Frame(nb,padding=12)
        nb.add(talk,text="🎃 Talking Pumpkin"); nb.add(vid,text="🎬 Custom Video")
        self.build_talk(talk); self.build_video(vid)
        ttk.Label(top,textvariable=self.status).pack(anchor="w",pady=(8,0))
        ttk.Button(top,text="Open Output Folder",command=lambda:os.startfile(OUTPUT)).pack(anchor="e")

    def common_output(self,parent,row):
        box=ttk.LabelFrame(parent,text="Pumpkin Filename / Slot",padding=8); box.grid(row=row,column=0,columnspan=4,sticky="ew",pady=8)
        ttk.Combobox(box,textvariable=self.slot,state="readonly",values=FACTORY,width=53).grid(row=0,column=0)
        ttk.Label(box,text="Custom name:").grid(row=0,column=1,padx=(12,4))
        ttk.Entry(box,textvariable=self.name,width=25).grid(row=0,column=2,sticky="ew"); box.columnconfigure(2,weight=1)

    def build_talk(self,p):
        missing=[n for n in FACE_NAMES if not (FACES/n.lower()/"preview.png").exists()]
        if missing:
            ttk.Label(p,text="Factory faces have not been imported. Run IMPORT_FACTORY_FACES.bat before using Talking Pumpkin.",foreground="red").grid(row=0,column=0,columnspan=4,sticky="w")
        cards=ttk.Frame(p); cards.grid(row=1,column=0,columnspan=4,sticky="ew",pady=8)
        for i,n in enumerate(FACE_NAMES):
            f=ttk.Frame(cards,padding=4,relief="ridge"); f.grid(row=0,column=i,padx=4,sticky="nsew"); cards.columnconfigure(i,weight=1)
            pp=FACES/n.lower()/"preview.png"
            if pp.exists():
                im=Image.open(pp).convert("RGB").rotate(180).resize((150,127),Image.Resampling.NEAREST)
                ph=ImageTk.PhotoImage(im); self.images[n]=ph; ttk.Label(f,image=ph).pack()
            ttk.Radiobutton(f,text=n,value=n,variable=self.face).pack()
        ttk.Label(p,text="Audio:").grid(row=2,column=0,sticky="w")
        ttk.Entry(p,textvariable=self.audio).grid(row=2,column=1,columnspan=2,sticky="ew",padx=5)
        ttk.Button(p,text="Browse…",command=self.pick_audio).grid(row=2,column=3)
        ttk.Label(p,text="Transcript / notes (optional; not currently used for timing):").grid(row=3,column=0,columnspan=4,sticky="w",pady=(8,0))
        self.transcript=tk.Text(p,height=5); self.transcript.grid(row=4,column=0,columnspan=4,sticky="nsew")
        pb=ttk.LabelFrame(p,text="End Pause",padding=8); pb.grid(row=5,column=0,columnspan=4,sticky="ew",pady=8)
        ttk.Spinbox(pb,from_=0,to=30,textvariable=self.pause,width=5).pack(side="left")
        ttk.Label(pb,text=" seconds   ").pack(side="left")
        ttk.Combobox(pb,textvariable=self.pause_mode,state="readonly",values=["Black","Idle Face","Idle + Expressions"],width=20).pack(side="left")
        ttk.Checkbutton(pb,text="Rotate final pumpkin AMV 180°",variable=self.rotate).pack(side="right")
        self.common_output(p,6)
        b=ttk.Frame(p); b.grid(row=7,column=0,columnspan=4,sticky="ew",pady=8)
        ttk.Button(b,text="Generate PC Preview",command=self.talk_preview).pack(side="left")
        ttk.Button(b,text="Generate Pumpkin AMV",command=self.talk_amv).pack(side="left",padx=8)
        p.columnconfigure(1,weight=1); p.columnconfigure(2,weight=1); p.rowconfigure(4,weight=1)

    def build_video(self,p):
        ttk.Label(p,text="Video:").grid(row=0,column=0,sticky="w")
        ttk.Entry(p,textvariable=self.video).grid(row=0,column=1,columnspan=2,sticky="ew",padx=5)
        ttk.Button(p,text="Browse…",command=self.pick_video).grid(row=0,column=3)
        opts=ttk.LabelFrame(p,text="Video Options",padding=10); opts.grid(row=1,column=0,columnspan=4,sticky="ew",pady=10)
        ttk.Label(opts,text="Fit:").grid(row=0,column=0,sticky="w")
        ttk.Combobox(opts,textvariable=self.fit,state="readonly",values=["Crop to Fill","Fit with Black Bars","Stretch"],width=20).grid(row=0,column=1,padx=5)
        ttk.Checkbutton(opts,text="Keep original audio",variable=self.keep_audio).grid(row=0,column=2,padx=15)
        ttk.Checkbutton(opts,text="Rotate final pumpkin AMV 180°",variable=self.rotate).grid(row=0,column=3)
        ttk.Label(opts,text="Start (seconds):").grid(row=1,column=0,sticky="w",pady=(8,0))
        ttk.Entry(opts,textvariable=self.trim_start,width=10).grid(row=1,column=1,sticky="w",pady=(8,0))
        ttk.Label(opts,text="End (seconds, blank = end):").grid(row=1,column=2,sticky="e",pady=(8,0))
        ttk.Entry(opts,textvariable=self.trim_end,width=10).grid(row=1,column=3,sticky="w",pady=(8,0))
        pb=ttk.LabelFrame(p,text="End Pause",padding=8); pb.grid(row=2,column=0,columnspan=4,sticky="ew")
        ttk.Spinbox(pb,from_=0,to=30,textvariable=self.pause,width=5).pack(side="left")
        ttk.Label(pb,text=" seconds   ").pack(side="left")
        ttk.Combobox(pb,textvariable=self.video_pause_mode,state="readonly",values=["Black","Hold Final Frame"],width=20).pack(side="left")
        self.common_output(p,3)
        info=ttk.Label(p,text="Output is automatically converted to 208×176, 15 fps, mono 22.05 kHz AMV for the pumpkin.",wraplength=760)
        info.grid(row=4,column=0,columnspan=4,sticky="w",pady=8)
        b=ttk.Frame(p); b.grid(row=5,column=0,columnspan=4,sticky="ew")
        ttk.Button(b,text="Generate PC Preview",command=self.video_preview).pack(side="left")
        ttk.Button(b,text="Generate Pumpkin AMV",command=self.video_amv).pack(side="left",padx=8)
        p.columnconfigure(1,weight=1); p.columnconfigure(2,weight=1)

    def pick_audio(self):
        x=filedialog.askopenfilename(filetypes=[("Audio","*.mp3 *.wav *.m4a *.aac"),("All","*.*")])
        if x:self.audio.set(x)
    def pick_video(self):
        x=filedialog.askopenfilename(filetypes=[("Video","*.mp4 *.mov *.avi *.mkv *.wmv *.m4v *.webm"),("All","*.*")])
        if x:self.video.set(x)
    def outname(self):
        x=self.slot.get().strip()
        if x!="Custom (11+)":return x
        n=self.name.get().strip() or "11_Custom.amv"
        return n if n.lower().endswith(".amv") else n+".amv"
    def run(self,cmd,msg):
        self.status.set(msg); self.update_idletasks()
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode: raise RuntimeError((r.stderr or r.stdout)[-1800:])
    def require_ffmpeg(self):
        if not self.ffmpeg: raise RuntimeError("FFmpeg is required. Install it or place ffmpeg.exe in the tools folder.")

    def audio_env(self,wav):
        with wave.open(str(wav),"rb") as w:
            rate=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)
        nf=max(1,math.ceil(len(x)/rate*FPS)); e=[]
        for i in range(nf):
            c=x[int(i/FPS*rate):min(len(x),int((i+1)/FPS*rate))]
            e.append(float(np.sqrt(np.mean(c*c))) if len(c) else 0)
        a=np.array(e); lo=np.percentile(a,20); hi=max(np.percentile(a,95),lo+1)
        return np.clip((a-lo)/(hi-lo),0,1)

    def render_talk(self,audio,device):
        self.require_ffmpeg()
        missing=[n for n in FACE_NAMES if not (FACES/n.lower()/"preview.png").exists()]
        if missing: raise RuntimeError("Factory faces are missing. Run IMPORT_FACTORY_FACES.bat first.")
        work=Path(tempfile.mkdtemp(prefix="jj_")); wav=work/"audio.wav"
        self.run([self.ffmpeg,"-y","-i",str(audio),"-ac","1","-ar","22050","-c:a","pcm_s16le",str(wav)],"Preparing audio…")
        env=self.audio_env(wav); fs=sorted((FACES/self.face.get().lower()).glob("state_*.png"))
        scored=sorted((float(np.array(Image.open(x).convert("L")).mean()),x) for x in fs); states=[x for _,x in scored]
        frames=work/"frames"; frames.mkdir(); last=0
        for i,e in enumerate(env):
            idx=0 if e<.08 else min(len(states)-1,max(1,int(e*(len(states)-1))))
            if i%2 and abs(idx-last)>2: idx=(idx+last)//2
            last=idx; im=Image.open(states[idx]).convert("RGB")
            if not device: im=im.rotate(180)
            im.save(frames/f"frame_{i:05d}.png")
        return work,wav,frames,states

    def talk_preview(self):
        a=Path(self.audio.get())
        if not a.exists(): return messagebox.showerror("Audio required","Choose audio first.")
        work=None
        try:
            work,wav,fr,_=self.render_talk(a,False); out=OUTPUT/f"{a.stem}_{self.face.get()}_preview.mp4"
            self.run([self.ffmpeg,"-y","-framerate","16","-i",str(fr/"frame_%05d.png"),"-i",str(wav),"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-shortest",str(out)],"Generating preview…")
            messagebox.showinfo("Finished",f"Created:\n{out}")
        except Exception as e: messagebox.showerror("Error",str(e))
        finally:
            if work: shutil.rmtree(work,ignore_errors=True)

    def talk_amv(self):
        a=Path(self.audio.get())
        if not a.exists(): return messagebox.showerror("Audio required","Choose audio first.")
        work=None
        try:
            work,wav,fr,states=self.render_talk(a,True); sec=max(0,min(30,int(self.pause.get()))); mode=self.pause_mode.get()
            start=len(list(fr.glob("frame_*.png"))); neutral=Image.open(states[0]).convert("RGB"); black=Image.new("RGB",(208,176))
            idle=states[:max(2,min(5,len(states)))]
            for j in range(sec*16):
                if mode=="Black": im=black.copy()
                elif mode=="Idle Face": im=neutral.copy()
                elif j%32 in (20,21,22,23) and len(idle)>1: im=Image.open(idle[1+(j//32)%(len(idle)-1)]).convert("RGB")
                else: im=neutral.copy()
                im.save(fr/f"frame_{start+j:05d}.png")
            pad=work/"pad.wav"
            with wave.open(str(wav),"rb") as r: params=r.getparams(); data=r.readframes(r.getnframes())
            with wave.open(str(pad),"wb") as w: w.setparams(params); w.writeframes(data); w.writeframes(bytes(22050*sec*2))
            vf=("hflip,vflip," if self.rotate.get() else "")+"fps=15"; out=OUTPUT/self.outname()
            self.run([self.ffmpeg,"-y","-framerate","16","-i",str(fr/"frame_%05d.png"),"-i",str(pad),"-vf",vf,"-c:v","amv","-pix_fmt","yuvj420p","-qmin","3","-qmax","3","-c:a","adpcm_ima_amv","-block_size","1470","-ar","22050","-ac","1","-shortest",str(out)],"Encoding pumpkin AMV…")
            messagebox.showinfo("Finished",f"Created:\n{out}")
        except Exception as e: messagebox.showerror("Error",str(e))
        finally:
            if work: shutil.rmtree(work,ignore_errors=True)

    def video_filter(self,preview=False):
        if self.fit.get()=="Crop to Fill": base="scale=208:176:force_original_aspect_ratio=increase,crop=208:176"
        elif self.fit.get()=="Fit with Black Bars": base="scale=208:176:force_original_aspect_ratio=decrease,pad=208:176:(ow-iw)/2:(oh-ih)/2:black"
        else: base="scale=208:176"
        # Preview is shown upright; device rotation is applied only to final AMV when selected.
        if preview: return base+",hflip,vflip"
        return base+(",hflip,vflip" if self.rotate.get() else "")

    def trim_args(self):
        try: start=max(0,float(self.trim_start.get() or 0))
        except: raise RuntimeError("Start time must be a number of seconds.")
        endtxt=self.trim_end.get().strip(); args=[]
        if start: args+=["-ss",str(start)]
        if endtxt:
            try: end=float(endtxt)
            except: raise RuntimeError("End time must be a number of seconds.")
            if end<=start: raise RuntimeError("End time must be greater than start time.")
            args+=["-t",str(end-start)]
        return args

    def video_preview(self):
        v=Path(self.video.get())
        if not v.exists(): return messagebox.showerror("Video required","Choose a video first.")
        try:
            self.require_ffmpeg(); out=OUTPUT/f"{v.stem}_preview.mp4"
            cmd=[self.ffmpeg,"-y"]+self.trim_args()+["-i",str(v),"-vf",self.video_filter(True),"-r","15","-c:v","libx264","-pix_fmt","yuv420p"]
            cmd += ["-c:a","aac","-ac","1","-ar","22050"] if self.keep_audio.get() else ["-an"]
            cmd += [str(out)]; self.run(cmd,"Generating custom-video preview…")
            messagebox.showinfo("Finished",f"Created:\n{out}")
        except Exception as e: messagebox.showerror("Error",str(e))

    def video_amv(self):
        v=Path(self.video.get())
        if not v.exists(): return messagebox.showerror("Video required","Choose a video first.")
        work=None
        try:
            self.require_ffmpeg(); work=Path(tempfile.mkdtemp(prefix="jjvideo_")); base=work/"base.mp4"
            # Normalize video and always create a 22050-Hz mono audio stream. If muted, use silence.
            targs=self.trim_args()
            if self.keep_audio.get():
                cmd=[self.ffmpeg,"-y"]+targs+["-i",str(v),"-vf",self.video_filter(False)+",fps=15","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-ac","1","-ar","22050","-shortest",str(base)]
            else:
                cmd=[self.ffmpeg,"-y"]+targs+["-i",str(v),"-f","lavfi","-i","anullsrc=r=22050:cl=mono","-vf",self.video_filter(False)+",fps=15","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-ar","22050","-ac","1","-shortest",str(base)]
            self.run(cmd,"Preparing custom video…")
            sec=max(0,min(30,int(self.pause.get()))); final=work/"final.mp4"
            if sec:
                # tpad extends video; apad supplies matching silence. clone = hold final frame, add = black.
                stopmode="clone" if self.video_pause_mode.get()=="Hold Final Frame" else "add"
                vf=f"tpad=stop_mode={stopmode}:stop_duration={sec}"
                self.run([self.ffmpeg,"-y","-i",str(base),"-vf",vf,"-af",f"apad=pad_dur={sec}","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-ar","22050","-ac","1","-shortest",str(final)],"Adding end pause…")
            else: final=base
            out=OUTPUT/self.outname()
            self.run([self.ffmpeg,"-y","-i",str(final),"-c:v","amv","-pix_fmt","yuvj420p","-qmin","3","-qmax","3","-r","15","-c:a","adpcm_ima_amv","-block_size","1470","-ar","22050","-ac","1","-shortest",str(out)],"Encoding pumpkin AMV…")
            messagebox.showinfo("Finished",f"Created:\n{out}\n\n208×176 • 15 fps • 22,050 Hz mono AMV")
        except Exception as e: messagebox.showerror("Error",str(e))
        finally:
            if work: shutil.rmtree(work,ignore_errors=True)

if __name__=="__main__": App().mainloop()
