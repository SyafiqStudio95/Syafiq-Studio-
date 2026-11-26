import sys, json, torch, soundfile as sf
from transformers import VitsModel, AutoTokenizer
m=VitsModel.from_pretrained("facebook/mms-tts-zlm"); t=AutoTokenizer.from_pretrained("facebook/mms-tts-zlm")
m.speaking_rate=float(sys.argv[3]); m.noise_scale=0.55; m.noise_scale_duration=0.7
L=json.load(open(sys.argv[1])); out=sys.argv[2]
for i,(sec,txt) in enumerate(L):
    torch.manual_seed(11)
    with torch.no_grad(): w=m(**t(txt,return_tensors="pt")).waveform[0].numpy()
    sf.write(f"{out}/l{i:02d}.wav",w,16000); print(i,sec,round(len(w)/16000,2))
