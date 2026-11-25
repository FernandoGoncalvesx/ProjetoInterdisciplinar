// Coordenadas relativas ao PNG recortado, não à foto original.
export function calcularEnquadramento(largura, altura, modelo, poses = []) {
    const w = modelo.foto_largura, h = modelo.foto_altura;
    let centro = largura / 2, base = altura, larguraTronco = largura;
    let automatico = false;
    const pontos = poses.length === 1 ? poses[0] : null;
    const visivel = p => p && Number.isFinite(p.x) && Number.isFinite(p.y)
        && p.x >= 0 && p.x <= 1 && p.y >= 0 && p.y <= 1
        && p.visibility >= .65 && (p.presence ?? 1) >= .65;
    if (pontos && [0, 11, 12].every(i => visivel(pontos[i]))) {
        const [rosto, esquerdo, direito] = [pontos[0], pontos[11], pontos[12]];
        const ombrosY = (esquerdo.y + direito.y) / 2;
        const ombros = Math.abs(esquerdo.x - direito.x) * largura;
        if (ombros > Math.max(2, largura * .03) && ombrosY > rosto.y) {
            centro = (esquerdo.x + direito.x) / 2 * largura;
            // Sem quadril visível, estima o tronco; o ajuste manual permanece disponível.
            const quadrilY = [23, 24].every(i => visivel(pontos[i]))
                ? (pontos[23].y + pontos[24].y) / 2
                : ombrosY + (ombrosY - rosto.y) * 2.8;
            if (quadrilY > ombrosY) {
                base = Math.min(altura, quadrilY * altura);
                larguraTronco = Math.min(largura, ombros * 1.65);
                automatico = true;
            }
        }
    }
    if (!automatico) centro = largura / 2;
    const escala = Math.min(w * .94 / larguraTronco, h * .94 / base);
    return {
        zoom: escala * largura / w,
        x: (largura / 2 - centro) * escala,
        y: h * .03,
        automatico,
    };
}

export async function detectarPose(imagem) {
    const bitmap = await createImageBitmap(imagem);
    let worker;
    try {
        worker = new Worker('/js/pose-worker.js');
        return await new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject(new Error('Tempo de detecção excedido')), 25000);
            worker.onmessage = ({data}) => {
                clearTimeout(timer);
                if (data.erro) reject(new Error(data.erro));
                else resolve(data.poses);
            };
            worker.onerror = () => {
                clearTimeout(timer);
                reject(new Error('Detecção indisponível'));
            };
            worker.postMessage(bitmap, [bitmap]);
        });
    } finally {
        worker?.terminate();
        bitmap.close();
    }
}
