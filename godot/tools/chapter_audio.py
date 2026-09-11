"""Original synthesized Gothic ambience and camera effects; no external recordings."""
import math,random,struct,wave
from pathlib import Path
rate=22050;root=Path('godot/assets/chapter/audio');root.mkdir(parents=True,exist_ok=True)
def write(name,seconds,fn):
 data=[]
 for i in range(round(seconds*rate)):
  t=i/rate;data.append(max(-.94,min(.94,fn(t))))
 with wave.open(str(root/(name+'.wav')),'wb') as w:
  w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(struct.pack('<%dh'%len(data),*(round(v*32767) for v in data)))
 print(name,'peak',round(max(map(abs,data)),3))
def sine(f,t):return math.sin(math.tau*f*t)
# Eight-second bars, a restrained D minor / B-flat / G minor / A suspended cycle.
chords=[[73.416,110,146.832,174.614],[58.27,87.307,116.54,146.832],[65.406,98,130.813,174.614],[55,82.407,110,146.832]]
def score(t):
 n=int(t//8)%4;u=t%8;env=min(1,u/1.7,(8-u)/1.7);notes=chords[n]
 organ=sum((sine(f,t)+.22*sine(f*2,t)+.08*sine(f*3,t)) for f in notes)*.027*max(0,env)
 bell=0
 for j in range(4):
  age=u-j*2
  if age>=0:
   f=notes[(j+n)%4]*4;bell+=(sine(f,age)+.24*sine(f*2.76,age))*math.exp(-age*2)*.035*min(1,age*90)
 return organ+bell
write('night',32,score)
write('capture',.9,lambda t:(sine(240+900*t,t)*.10+sine(480+1100*t,t)*.035)*math.sin(math.pi*t/.9)**2)
write('super',1.1,lambda t:(sine(80+140*t,t)*.14+sine(360+1100*t,t)*.08+sine(540+1400*t,t)*.04)*math.sin(math.pi*t/1.1)**2)
