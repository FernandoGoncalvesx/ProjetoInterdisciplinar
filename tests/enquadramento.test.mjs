import {test} from 'node:test';
import assert from 'node:assert/strict';
import {calcularEnquadramento, detectarPose} from '../frontend/js/enquadramento.js';

const modelo = {foto_largura: 210, foto_altura: 255};
const pose = () => {
    const p = Array.from({length: 33}, () => ({x: .5, y: .5, visibility: 0}));
    for (const [i, x, y] of [[0,.6,.12], [11,.45,.25], [12,.75,.25], [23,.48,.55], [24,.72,.55]]) {
        p[i] = {x, y, visibility: .95};
    }
    return p;
};
test('sem pose mantém toda a pessoa dentro do card', () => {
    for (const [w,h] of [[400,1600], [1600,400], [700,1000]]) {
        const r = calcularEnquadramento(w,h,modelo);
        const escala = r.zoom * modelo.foto_largura / w;
        assert.ok(w * escala <= modelo.foto_largura);
        assert.ok(h * escala + r.y <= modelo.foto_altura);
        assert.equal(r.automatico, false);
    }
});
test('centraliza ombros deslocados e enquadra até o quadril', () => {
    const r = calcularEnquadramento(1000,1600,modelo,[pose()]);
    const escala = r.zoom * 210 / 1000;
    assert.equal(r.automatico,true);
    assert.ok(Math.abs(105 + (600-500)*escala + r.x - 105) < .001);
    assert.ok(.55*1600*escala + r.y <= 255);
});
test('pontos ausentes, inválidos e múltiplas pessoas usam ajuste básico', () => {
    for (const poses of [[], [[],[]], [[]]]) {
        assert.equal(calcularEnquadramento(800,1200,modelo,poses).automatico,false);
    }
    const p=pose(); p[0].x=NaN;
    assert.equal(calcularEnquadramento(800,1200,modelo,[p]).automatico,false);
});
test('estima tronco sem quadril visível', () => {
    const p=pose(); p[23].visibility=p[24].visibility=0;
    assert.equal(calcularEnquadramento(800,1200,modelo,[p]).automatico,true);
});
test('aceita ombros confiáveis em foto larga com braços abertos', () => {
    const p=pose(); p[11].x=.54; p[12].x=.455;
    assert.equal(calcularEnquadramento(1000,667,modelo,[p]).automatico,true);
});
test('falha do worker libera recursos e permite fallback', async () => {
    let encerrado=false, fechado=false;
    globalThis.createImageBitmap=async () => ({close(){fechado=true;}});
    globalThis.Worker=class {
        postMessage(){queueMicrotask(() => this.onmessage({data:{erro:'indisponível'}}));}
        terminate(){encerrado=true;}
    };
    await assert.rejects(detectarPose({}), /indisponível/);
    assert.ok(encerrado && fechado);
    delete globalThis.Worker;
    delete globalThis.createImageBitmap;
});
