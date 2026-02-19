export async function recordOnce(ms = 3000) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);

    const processor = audioCtx.createScriptProcessor(4096, 1, 1);
    const samples = [];

    processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);
        // Copy the data so we don't hold onto the internal buffer
        samples.push(new Float32Array(input));
    };

    source.connect(processor);
    processor.connect(audioCtx.destination);

    return new Promise((resolve, reject) => {
        setTimeout(async () => {
            try {
                // Stop everything
                processor.disconnect();
                source.disconnect();
                stream.getTracks().forEach((t) => t.stop());

                // Flatten samples into one Float32Array
                let length = 0;
                for (const s of samples) length += s.length;
                const pcm = new Float32Array(length);
                let offset = 0;
                for (const s of samples) {
                    pcm.set(s, offset);
                    offset += s.length;
                }

                const wavBlob = float32ToWavBlob(pcm, audioCtx.sampleRate);
                resolve(wavBlob);
            } catch (err) {
                reject(err);
            } finally {
                audioCtx.close();
            }
        }, ms);
    });
}

export function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const dataUrl = reader.result;
            const base64 = String(dataUrl).split(",")[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

function float32ToWavBlob(float32Array, sampleRate) {
    const bytesPerSample = 2;
    const numChannels = 1;
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataLength = float32Array.length * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataLength);
    const view = new DataView(buffer);

    let offset = 0;

    function writeString(view, offset, str) {
        for (let i = 0; i < str.length; i++) {
            view.setUint8(offset + i, str.charCodeAt(i));
        }
    }

    // RIFF header
    writeString(view, offset, "RIFF"); offset += 4;
    view.setUint32(offset, 36 + dataLength, true); offset += 4;
    writeString(view, offset, "WAVE"); offset += 4;

    // fmt chunk
    writeString(view, offset, "fmt "); offset += 4;
    view.setUint32(offset, 16, true); offset += 4;   // PCM chunk size
    view.setUint16(offset, 1, true); offset += 2;    // audio format = PCM
    view.setUint16(offset, numChannels, true); offset += 2;
    view.setUint32(offset, sampleRate, true); offset += 4;
    view.setUint32(offset, byteRate, true); offset += 4;
    view.setUint16(offset, blockAlign, true); offset += 2;
    view.setUint16(offset, 16, true); offset += 2;   // bits per sample

    // data chunk
    writeString(view, offset, "data"); offset += 4;
    view.setUint32(offset, dataLength, true); offset += 4;

    // PCM samples
    let outOffset = offset;
    for (let i = 0; i < float32Array.length; i++, outOffset += 2) {
        let s = Math.max(-1, Math.min(1, float32Array[i]));
        view.setInt16(outOffset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }

    return new Blob([buffer], { type: "audio/wav" });
}
