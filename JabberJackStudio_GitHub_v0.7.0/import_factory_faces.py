from pathlib import Path
import subprocess, shutil, tempfile, sys
import numpy as np
from PIL import Image
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:
    tk=None

ROOT=Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
OUT=ROOT/'assets'/'faces'
TOOLS=ROOT/'tools'

SOURCE_PATTERNS={
    'traditional':['02_Audio Adjusted Traditional Pumpkin Singing_1.amv','03_Traditional Pumpkin Emotions.amv'],
    'funny':['07_0Funny_VO_2E.amv'],
    'scary':['06_Scary Pumpkin Emotions.amv','06_Scary Pumpkin Emotions(1).amv','05_Audio Adjusted Scary Pumpkin Singing_1.amv'],
    'angry':['04_Angry_VO_2E.amv'],
}

def ffmpeg_path():
    bundled=TOOLS/'ffmpeg.exe'
    return str(bundled) if bundled.exists() else shutil.which('ffmpeg')

def locate(folder,names):
    files={p.name.lower():p for p in folder.iterdir() if p.is_file()}
    for n in names:
        if n.lower() in files:return files[n.lower()]
    return None

def extract(src,dest,ffmpeg):
    shutil.rmtree(dest,ignore_errors=True); dest.mkdir(parents=True)
    temp=Path(tempfile.mkdtemp(prefix='jack_faces_'))
    try:
        subprocess.run([ffmpeg,'-y','-i',str(src),'-vf','fps=4',str(temp/'f_%05d.png')],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
        files=sorted(temp.glob('*.png'))
        if not files: raise RuntimeError(f'No frames decoded from {src.name}')
        prev=None; scored=[]
        for i,f in enumerate(files):
            a=np.asarray(Image.open(f).convert('L'),dtype=np.int16)
            activity=float(a.mean())
            diff=0.0 if prev is None else float(np.abs(a-prev).mean())
            scored.append((activity+2*diff,i,f))
            prev=a
        scored.sort(reverse=True)
        chosen=[]
        for score,i,f in scored:
            if all(abs(i-j)>8 for _,j,_ in chosen): chosen.append((score,i,f))
            if len(chosen)>=12: break
        if len(chosen)<4: raise RuntimeError(f'Not enough distinct frames in {src.name}')
        chosen.sort(key=lambda x:x[1])
        for n,(_,_,f) in enumerate(chosen): shutil.copy2(f,dest/f'state_{n:02d}.png')
        best=max(chosen,key=lambda x:x[0])[2]
        shutil.copy2(best,dest/'preview.png')
    finally: shutil.rmtree(temp,ignore_errors=True)

def main():
    ff=ffmpeg_path()
    if not ff:
        raise RuntimeError('FFmpeg was not found. Install FFmpeg or place ffmpeg.exe in app\\tools.')
    cli_mode=len(sys.argv)>1
    if cli_mode:
        folder=Path(sys.argv[1])
    elif tk:
        r=tk.Tk(); r.withdraw()
        selected=filedialog.askdirectory(title="Select folder containing your original Jabberin' Jack AMV files")
        r.destroy()
        if not selected:return
        folder=Path(selected)
    else: raise RuntimeError('Pass the folder containing the original AMV files.')
    missing=[]; found={}
    for face,names in SOURCE_PATTERNS.items():
        f=locate(folder,names)
        if f: found[face]=f
        else: missing.append(face)
    if missing:
        raise RuntimeError('Could not find source AMVs for: '+', '.join(missing))
    for face,src in found.items():
        print(f'Importing {face}: {src.name}')
        extract(src,OUT/face,ff)
    msg='Factory faces imported successfully. You can now run the generator.'
    print(msg)
    if tk and not cli_mode:
        r=tk.Tk(); r.withdraw(); messagebox.showinfo('Import complete',msg); r.destroy()

if __name__=='__main__':
    try: main()
    except Exception as e:
        print('ERROR:',e)
        if tk and len(sys.argv)<=1:
            try:
                r=tk.Tk(); r.withdraw(); messagebox.showerror('Import failed',str(e)); r.destroy()
            except Exception:
                pass
        sys.exit(1)
