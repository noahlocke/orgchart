const RAW=require('./orgdata.json');
const CW=210,CH=56,VGAP=16,HGAP=30,DROP=40,ROOTGAP=70,PRIMARY="Noah Locke";
const byName=new Map(); RAW.forEach(r=>byName.set(r.name,{name:r.name,cls:r.cls,mgr:r.mgr,children:[]}));
const roots=[]; byName.forEach(n=>{const p=n.mgr&&byName.get(n.mgr); if(p)p.children.push(n); else if(!byName.has(n.mgr)) roots.push({name:n.mgr,cls:"root",children:[n],synthetic:true});});
const rootMap=new Map(),realRoots=[]; roots.forEach(r=>{if(rootMap.has(r.name))rootMap.get(r.name).children.push(...r.children);else{rootMap.set(r.name,r);realRoots.push(r);}});
realRoots.sort((a,b)=>a.name===PRIMARY?-1:b.name===PRIMARY?1:a.name.localeCompare(b.name));
function sortKids(n){n.children.sort((a,b)=>{const am=a.children.length>0,bm=b.children.length>0;if(am!==bm)return am?1:-1;return a.name.localeCompare(b.name);});n.children.forEach(sortKids);} realRoots.forEach(sortKids);
const expanded=new Set();
const hasKids=n=>n.children.length>0, isOpen=n=>expanded.has(n.name);
function layout(n,x,y){
  if(!hasKids(n)||!isOpen(n)){n.bx=x;n.by=y;n.bw=CW;n.bh=CH;n.x=x;n.y=y;return{w:CW,h:CH};}
  const ics=n.children.filter(c=>!hasKids(c)), mgrs=n.children.filter(c=>hasKids(c));
  const childTop=y+CH+DROP; let icW=0,icH=0; if(ics.length){icW=CW;icH=ics.length*CH+(ics.length-1)*VGAP;}
  let mgrW=0,mgrH=0; const mb=[]; if(mgrs.length){let cx=0;mgrs.forEach((m,i)=>{const b=layout(m,cx,0);mb.push(b);cx+=b.w+(i<mgrs.length-1?HGAP:0);mgrH=Math.max(mgrH,b.h);});mgrW=cx;}
  const childW=Math.max(icW,mgrW,CW); const childLeft=x+(Math.max(CW,childW)-childW)/2; const subW=Math.max(CW,childW);
  let yy=childTop; if(ics.length){const icLeft=childLeft+(childW-icW)/2; ics.forEach(c=>{layout(c,icLeft,yy);yy+=CH+VGAP;}); yy=childTop+icH+(mgrs.length?VGAP:0);}
  if(mgrs.length){const mgrLeft=childLeft+(childW-mgrW)/2; let cx=mgrLeft; mgrs.forEach((m,i)=>{const b=mb[i]; shift(m,cx-m.bx,yy-m.by); cx+=b.w+HGAP;});}
  const subH=CH+DROP+(icH+(ics.length&&mgrs.length?VGAP:0)+mgrH);
  n.bx=x;n.by=y;n.bw=subW;n.bh=subH;n.x=x+(subW-CW)/2;n.y=y;return{w:subW,h:subH};
}
function shift(n,dx,dy){n.x+=dx;n.y+=dy;n.bx+=dx;n.by+=dy;if(hasKids(n)&&isOpen(n))n.children.forEach(c=>shift(c,dx,dy));}
function runLayout(){let cx=0,maxH=0;realRoots.forEach(r=>{const b=layout(r,cx,0);cx+=b.w+ROOTGAP;maxH=Math.max(maxH,b.h);});return{x:0,y:0,w:Math.max(0,cx-ROOTGAP),h:maxH};}
function visible(){const out=[];(function w(n){if(!n.synthetic)out.push(n);if(hasKids(n)&&isOpen(n))n.children.forEach(w);})(realRoots[0]);realRoots.slice(1).forEach(r=>{(function w(n){if(!n.synthetic)out.push(n);if(hasKids(n)&&isOpen(n))n.children.forEach(w);})(r);});return out;}
function overlaps(){const v=visible();let bad=0,pairs=0;for(let i=0;i<v.length;i++)for(let j=i+1;j<v.length;j++){pairs++;const a=v[i],b=v[j];const ox=a.x< b.x+CW && b.x< a.x+CW; const oy=a.y< b.y+CH && b.y< a.y+CH; if(ox&&oy){bad++; if(bad<=5)console.log('  OVERLAP',a.name,'<>',b.name, JSON.stringify({ax:a.x|0,ay:a.y|0,bx:b.x|0,by:b.y|0}));}}return{bad,count:v.length,pairs};}
function pos(){return visible().every(n=>Number.isFinite(n.x)&&Number.isFinite(n.y));}

function test(label){const W=runLayout();const r=overlaps();console.log(label.padEnd(34),'nodes='+String(r.count).padStart(4),'overlaps='+r.bad,'allPositioned='+pos(),'world='+(W.w|0)+'x'+(W.h|0));return r.bad;}

let fails=0;
// State A: only roots
realRoots.forEach(r=>expanded.add(r.name)); fails+=test('A roots only');
// State B: primary one level
fails+=test('B roots only (dup)');
// State C: expand a mix - Noah subtree fully + others collapsed
function expAll(n){if(n.children.length)expanded.add(n.name);n.children.forEach(expAll);}
expanded.clear(); realRoots.forEach(r=>expanded.add(r.name)); expAll(rootMap.get(PRIMARY)); fails+=test('C primary fully expanded');
// State D: EVERYTHING expanded (worst case width reflow)
expanded.clear(); realRoots.forEach(r=>{expanded.add(r.name);expAll(r);}); fails+=test('D fully expanded (all roots)');
// State E: deep single chain Noah>Rafael>Jeneane>James
expanded.clear(); ['Noah Locke','Hugh Fetner','Mandy Benny','Ron Hardin','Noah Locke','Rafael Santander','Jeneane Hubbell','James Stiner'].forEach(x=>byName.get(x)&&expanded.add(x)); realRoots.forEach(r=>expanded.add(r.name)); fails+=test('E deep chain');

// Fit math sanity
function fit(b,vwv,vhv,pad=60){const k=Math.max(0.04,Math.min(2.4,Math.min((vwv-2*pad)/b.w,(vhv-2*pad)/b.h)));const tx=vwv/2-k*(b.x+b.w/2),ty=vhv/2-k*(b.y+b.h/2);
  const cxw=b.x+b.w/2, scr=k*cxw+tx; return {k:+k.toFixed(4), centeredX:Math.abs(scr-vwv/2)<1e-6};}
const W=runLayout(); const f=fit(W,1440,900);
console.log('\nFit world @1440x900 -> k='+f.k+' centered='+f.centeredX);
// verify IC-above-manager ordering for a node with both
const lilly=byName.get('Lilly Dang'); expanded.clear(); realRoots.forEach(r=>expanded.add(r.name)); expanded.add('Lilly Dang'); runLayout();
const lk=lilly.children; const ics=lk.filter(c=>!hasKids(c)), mg=lk.filter(c=>hasKids(c));
const maxIcY=Math.max(...ics.map(c=>c.y)), minMgY=Math.min(...mg.map(c=>c.y));
console.log('Lilly Dang: ICs(',ics.length,') topY range, max IC y='+(maxIcY|0)+' ; managers('+mg.length+') min y='+(minMgY|0)+' -> ICs above managers:', maxIcY<minMgY);

console.log('\nTOTAL OVERLAP FAILURES:',fails);
process.exit(fails?1:0);
