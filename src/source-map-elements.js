/** Merge only the explicit, hash-bound binary property supplement.
 * Unknown native flags remain null; this does not approve special mechanics.
 */
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function requireValue(ok,message){if(!ok){const error=new Error(message);error.code='SOURCE_ELEMENT_SUPPLEMENT';throw error;}}
export function mergeSourceMapElements(base,supplement,{baseCatalogSha256}={}){
  requireValue(Array.isArray(base?.elements)&&Array.isArray(supplement?.elements),'Missing source element arrays');
  requireValue(baseCatalogSha256===supplement.baseElementCatalogSha256,'Baseline element SHA differs from supplement evidence');
  requireValue(base.elements.length===supplement.expectedBaseElementCount,'Baseline element count differs');
  requireValue(supplement.elements.length===supplement.expectedAdditionalElementCount,'Supplement count differs');
  const ids=new Set();
  for(const element of base.elements){requireValue(Number.isInteger(element.id)&&!ids.has(element.id),'Duplicate baseline element ID');ids.add(element.id);}
  for(const element of supplement.elements){
    const raw=element.binaryPropertyRecord,props=element.properties;
    requireValue(Number.isInteger(element.id)&&!ids.has(element.id),'Supplement ID conflicts with an existing element');
    requireValue(raw&&raw.id===element.id,'Supplement lacks its own binary record');
    requireValue(Number.isInteger(element.widthCells)&&element.widthCells>0&&Number.isInteger(element.heightCells)&&element.heightCells>0,'Invalid supplemental footprint');
    requireValue(element.widthCells===raw.widthCells&&element.heightCells===raw.heightCells&&same(element.imageOffset,raw.offsetRaw)&&same(element.gridAttr,raw.gridAttrRaw),'Supplement geometry differs from binary record');
    requireValue(Array.isArray(element.imageOffset)&&element.imageOffset.length===2&&element.imageOffset.every(Number.isInteger),'Invalid supplemental offset');
    requireValue(element.gridAttr.length===element.widthCells*element.heightCells&&element.gridAttr.every(v=>Number.isInteger(v)&&v>=0&&v<=0xffffffff),'Invalid supplemental GridAttr');
    requireValue(props&&props.imageID===element.id&&same(props.size,[raw.widthCells,raw.heightCells])&&props.LifeTime===raw.lifeTimeRaw&&props.Level===raw.wordAtRecord16&&props.canMove===raw.wordAtRecord20,'Supplement properties differ from binary record');
    requireValue(Number.isInteger(props.LifeTime)&&Number.isInteger(props.canMove)&&Number.isInteger(props.Level),'Invalid supplemental properties');
    requireValue(props.canDoSpecial===null&&props.canHide===null,'Unserialized native flags must remain unknown');
    ids.add(element.id);
  }
  requireValue(same([...supplement.elements.map(e=>e.id)].sort((a,b)=>a-b),supplement.additionalIds),'Supplement IDs differ from explicit source list');
  return {...base,elementCount:ids.size,elements:[...base.elements,...supplement.elements],definitionSupplement:{
    source:supplement.source,additionalIds:[...supplement.additionalIds],unknownUnserializedFields:[...supplement.unknownUnserializedFields],
    status:'community-binary-definitions-only; special mechanisms and original authenticity unverified',
  }};
}
