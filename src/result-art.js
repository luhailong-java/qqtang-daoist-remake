const states=Object.freeze({
  victory:Object.freeze({id:'victory',label:'胜利',file:'assets/ui/results/victory.png'}),
  draw:Object.freeze({id:'draw',label:'平局',file:'assets/ui/results/draw.png'}),
  defeat:Object.freeze({id:'defeat',label:'再接再厉',file:'assets/ui/results/defeat.png'})
});

// The authoritative winner selects the artwork; pending/invalid outcomes are not losses.
export function resultPresentation(winnerTeam,playerTeam){
  if(!['red','blue'].includes(playerTeam))return null;
  if(winnerTeam==='draw')return states.draw;
  if(!['red','blue'].includes(winnerTeam))return null;
  return states[winnerTeam===playerTeam?'victory':'defeat'];
}
