// Diagnostic adapters only. Raw offsets retain their source meaning; these are not gameplay bindings.
export const sequenceCategories = new Set(['effects', 'pickupSequences', 'headWorld', 'headWorld114', 'headWorld39', 'backWorld', 'mapSequences', 'characterMotion']);
export function headWorldSequences(data, sourceClass = 'thadorn') {
  return data.items.map(item => ({
    ...item, sourceResource: `${sourceClass}-${item.itemId}`, projectEffectName: item.projectDisplayName??item.sourceName,
    frameCount: item.frames.length, sourceDeclaredFrameCount: item.sourceFrameCount,
    frames: item.frames.map(f => ({...f, frameIndex: f.sourceFrameIndex,
      sourceFrame: {width: f.logicalFrameSize[0], height: f.logicalFrameSize[1], frameOffset: f.frameOffsetRaw}})),
    diagnosticNote: `原始frameOffset相对包络预览；方向语义、${sourceClass === 'npack' ? '背部' : '头部'}绑定与播放时序未知。`,
  }));
}
export function sequenceFrameLabel(clip){
  return clip.sourceDeclaredFrameCount!==undefined&&clip.sourceDeclaredFrameCount!==clip.frameCount
    ?`${clip.frameCount} / 源${clip.sourceDeclaredFrameCount}帧`:`${clip.frameCount} 帧`;
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

export function characterDiagnosticSequence(data) {
  const actor = {'daoist-child': '道童', 'moon-shadow': '月影'}[data.characterId] ?? data.characterId;
  const direction = {N: '北向', E: '东向', S: '南向', W: '西向'}[data.direction] ?? data.direction;
  return {
    ...data,
    sourceResource: `${data.characterId}-${data.direction}`,
    projectEffectName: `${actor} · ${direction}步行`,
    frameCount: data.frames.length,
    sourceDeclaredFrameCount: data.sourceFrameOrder.length,
    frames: data.frames.map(frame => ({
      ...frame,
      frameIndex: frame.sourceFrameIndex,
      sourceFrame: {width: frame.width, height: frame.height, frameOffset: [0, 0]},
    })),
    diagnosticNote: '按已对齐的256像素审阅画布展示。各源分层偏移见来源记录，原时序和人物根点待核。',
  };
}
