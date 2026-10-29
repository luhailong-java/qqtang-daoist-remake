// Diagnostic adapters only. Raw offsets retain their source meaning; these are not gameplay bindings.
export const sequenceCategories = new Set(['effects', 'pickupSequences', 'headWorld', 'mapSequences']);
export function headWorldSequences(data) {
  return data.items.map(item => ({
    ...item, sourceResource: `thadorn-${item.itemId}`, projectEffectName: item.sourceName,
    frameCount: item.sourceFrameCount,
    frames: item.frames.map(f => ({...f, frameIndex: f.sourceFrameIndex,
      sourceFrame: {width: f.logicalFrameSize[0], height: f.logicalFrameSize[1], frameOffset: f.frameOffsetRaw}})),
    diagnosticNote: '原始frameOffset相对包络预览；方向语义、头部绑定与播放时序未知。',
  }));
}
export function mapSequence(data) {
  return {...data, sourceResource: `map-${data.elementId}`,
    projectEffectName: `${data.family} · ${data.elementId}`, frameCount: data.sourceDeclaredFrameCount,
    frames: data.frames.map(f => ({...f, ...f.exports?.['4'], frameIndex: f.sourceFrameIndex,
      empty: Boolean(f.structuralEmpty || f.sourceFullyTransparentPixels),
      reuseOfFrameIndex: f.pixelAliasOfFrameIndex ?? undefined,
      sourceFrame: {width: f.sourceFrameSize[0], height: f.sourceFrameSize[1], frameOffset: f.sourceFrameOffset}})),
    diagnosticNote: '仅frameOffset相对包络；mapElemOffset另存，未合成未经证实的运行锚点。',
  };
}
