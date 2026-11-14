// Diagnostic adapters only. Raw offsets retain their source meaning; these are not gameplay bindings.
export const sequenceCategories = new Set(['effects', 'pickupSequences', 'headWorld', 'headWorld114', 'headWorld39', 'backWorld', 'wingWorld', 'entryWorld', 'mapSequences', 'characterMotion']);
export function entryWorldSequence(data) {
  return {
    sourceResource: `enter${data.resourceId}_stand`, projectEffectName: data.projectDisplayName,
    frameCount: data.positions.length, originalFrameDurationMs: null,
    diagnosticNote: '原资源是满幅不透明图。按源偏移显示，入场触发、层次和时序待核。',
    frames: data.positions.map(p => ({...p, frameIndex: p.index,
      sourceFrame: {width: p.sourceSize[0], height: p.sourceSize[1], frameOffset: p.sourceRawOffset}})),
  };
}
export function wingWorldSequences(data) {
  return Object.entries(data.memberPositions).map(([kind, positions]) => {
    const originals = new Map();
    return {
      sourceResource: `fpack${data.resourceId}_${kind}`,
      projectEffectName: `${data.projectDisplayName} · ${kind === 'stand' ? '站立源位置' : '行走源位置'}`,
      frameCount: positions.length,
      originalFrameDurationMs: null,
      diagnosticNote: '两份源资源字节相同。按源偏移展示，视向、实际佩戴锚点和时序待核。',
      frames: positions.map((position, ordinal) => {
        const first = originals.get(position.uniqueRasterIndex);
        if (first === undefined) originals.set(position.uniqueRasterIndex, ordinal);
        return {
          ...position.candidate, frameIndex: position.index, reuseOfFrameIndex: first,
          sourceFrame: {width: position.sourceSize[0], height: position.sourceSize[1], frameOffset: position.sourceRawOffset},
        };
      }),
    };
  });
}
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
  const actor = {'daoist-child': '道童', 'moon-shadow': '月影', 'mountain-guardian': '山岳'}[data.characterId] ?? data.characterId;
  const direction = {N: '北向', E: '东向', S: '南向', W: '西向'}[data.direction] ?? data.direction;
  const previewPosition = new Map(data.frames.map((frame, index) => [frame.sourceFrameIndex, index]));
  return {
    ...data,
    sourceResource: `${data.characterId}-${data.direction}`,
    projectEffectName: `${actor} · ${direction}步行`,
    frameCount: data.frames.length,
    sourceDeclaredFrameCount: data.sourceFrameOrder.length,
    originalFrameDurationMs: data.originalFrameDurationMs ?? data.sourceFrameDurationMs ?? null,
    frames: data.frames.map(frame => ({
      ...frame,
      frameIndex: frame.sourceFrameIndex,
      reuseOfFrameIndex: previewPosition.get(frame.rasterAliasOfSourceFrameIndex),
      sourceFrame: {width: frame.width, height: frame.height, frameOffset: [0, 0]},
    })),
    diagnosticNote: '按已对齐的256像素审阅画布展示。各源分层偏移见来源记录，原时序和人物根点待核。',
  };
}
