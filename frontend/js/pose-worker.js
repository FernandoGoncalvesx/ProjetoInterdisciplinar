// A foto permanece no navegador. Apenas biblioteca, WASM e modelo são baixados.
self.onmessage = async ({data: imagem}) => {
    let detector;
    try {
        const {FilesetResolver, PoseLandmarker} = await import(
            'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.32/vision_bundle.mjs');
        const vision = await FilesetResolver.forVisionTasks(
            'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.32/wasm');
        detector = await PoseLandmarker.createFromOptions(vision, {
            baseOptions: {
                modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
                delegate: 'CPU',
            },
            runningMode: 'IMAGE',
            numPoses: 2,
            minPoseDetectionConfidence: .6,
            minPosePresenceConfidence: .6,
        });
        const canvas = new OffscreenCanvas(imagem.width, imagem.height);
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(imagem, 0, 0);
        self.postMessage({poses: detector.detect(canvas).landmarks});
    } catch (erro) {
        self.postMessage({erro: 'Não foi possível detectar o enquadramento.'});
    } finally {
        detector?.close();
        imagem.close();
    }
};
