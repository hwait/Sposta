var ct = 0;
var lastwon = 0;
var psv = [{ sc: 0 }, { sc: 0 }];

function StatInit() {
    TypePressed(0);
}
function ScorePressed(pn) {
    lastwon = pn;
    if (psv[pn].sc < 1)
        psv[pn].sc++;
    else
        psv[pn].sc--;
    visualize();
}

function TypePressed(n) {
    document.getElementById("st" + ct).style.backgroundColor = document.getElementById("st" + n).style.backgroundColor;
    document.getElementById("st" + n).style.backgroundColor = "#0d47a1";
    ct = n;
    visualize();
}
function calc(n) {
    if (psv[0].sc == 1 && psv[1].sc == 1 && lastwon == 0) {
        psv[0].mtp = pss[0][ct].s1ls2w;
        psv[0].mtw = pss[0][ct].s1ls2w - pss[0][ct].s1ls2wml;
        psv[0].mtl = pss[0][ct].s1ls2wml;
        psv[0].stw = pss[0][ct].s1ls2w - pss[0][ct].s1ls2wml;
        psv[0].stl = pss[0][ct].s1ls2wml;
        psv[1].mtp = pss[1][ct].s1ws2l;
        psv[1].mtw = pss[1][ct].s1ws2lmw;
        psv[1].mtl = pss[1][ct].s1ws2l - pss[1][ct].s1ws2lmw;
        psv[1].stw = pss[1][ct].s1ws2lmw;
        psv[1].stl = pss[1][ct].s1ws2l - pss[1][ct].s1ws2lmw;
    }
    if (psv[0].sc == 1 && psv[1].sc == 1 && lastwon == 1) {
        psv[0].mtp = pss[0][ct].s1ws2l;
        psv[0].mtw = pss[0][ct].s1ws2lmw;
        psv[0].mtl = pss[0][ct].s1ws2l - pss[0][ct].s1ws2lmw;
        psv[0].stw = pss[0][ct].s1ws2lmw;
        psv[0].stl = pss[0][ct].s1ws2l - pss[0][ct].s1ws2lmw;
        psv[1].mtp = pss[1][ct].s1ls2w;
        psv[1].mtw = pss[1][ct].s1ls2w - pss[1][ct].s1ls2wml;
        psv[1].mtl = pss[1][ct].s1ls2wml;
        psv[1].stw = pss[1][ct].s1ls2w - pss[1][ct].s1ls2wml;
        psv[1].stl = pss[1][ct].s1ls2wml;
    }
    if (psv[0].sc == 1 && psv[1].sc == 0) {
        psv[0].mtp = pss[0][ct].s1w;
        psv[0].mtw = pss[0][ct].s1w - pss[0][ct].s1wml;
        psv[0].mtl = pss[0][ct].s1wml;
        psv[0].stw = pss[0][ct].s1w - pss[0][ct].s1ws2l;
        psv[0].stl = pss[0][ct].s1ws2l;

        psv[1].mtp = pss[1][ct].s1l;
        psv[1].mtw = pss[1][ct].s1lmw;
        psv[1].mtl = pss[1][ct].s1l - pss[1][ct].s1lmw;
        psv[1].stw = pss[1][ct].s1ls2w;
        psv[1].stl = pss[1][ct].s1l - pss[1][ct].s1ls2w;
    }
    if (psv[0].sc == 0 && psv[1].sc == 1) {
        psv[0].mtp = pss[0][ct].s1l;
        psv[0].mtw = pss[0][ct].s1lmw;
        psv[0].mtl = pss[0][ct].s1l - pss[0][ct].s1lmw;
        psv[0].stw = pss[0][ct].s1ls2w;
        psv[0].stl = pss[0][ct].s1l - pss[0][ct].s1ls2w;
        psv[1].mtp = pss[1][ct].s1w;
        psv[1].mtw = pss[1][ct].s1w - pss[1][ct].s1wml;
        psv[1].mtl = pss[1][ct].s1wml;
        psv[1].stw = pss[1][ct].s1w - pss[1][ct].s1ws2l;
        psv[1].stl = pss[1][ct].s1ws2l;
    }
    if (psv[0].sc == 0 && psv[1].sc == 0) {
        psv[0].mtp = pss[0][ct].tp;
        psv[0].mtw = pss[0][ct].tw;
        psv[0].mtl = pss[0][ct].tp - pss[0][ct].tw;
        psv[0].stw = pss[0][ct].s1w;
        psv[0].stl = pss[0][ct].s1l;
        psv[1].mtp = pss[1][ct].tp;
        psv[1].mtw = pss[1][ct].tw;
        psv[1].mtl = pss[1][ct].tp - pss[1][ct].tw;
        psv[1].stw = pss[1][ct].s1w;
        psv[1].stl = pss[1][ct].s1l;
    }
    w = psv[0].mtw / psv[0].mtp;
    l = psv[0].mtl / psv[0].mtp;
    psv[0].mcw = getColor(w);
    psv[0].mcl = getColor(l);
    psv[0].mpw = pct(w * 100, 1);
    psv[0].mpl = pct(l * 100, 1);
    psv[0].mow = pct(1 / w, 2);
    psv[0].mol = pct(1 / l, 2);
    w = psv[0].stw / psv[0].mtp;
    l = psv[0].stl / psv[0].mtp;
    psv[0].scw = getColor(w);
    psv[0].scl = getColor(l);
    psv[0].spw = pct(w * 100, 1);
    psv[0].spl = pct(l * 100, 1);
    psv[0].sow = pct(1 / w, 2);
    psv[0].sol = pct(1 / l, 2);
    w = psv[1].mtw / psv[1].mtp;
    l = psv[1].mtl / psv[1].mtp;
    psv[1].mcw = getColor(w);
    psv[1].mcl = getColor(l);
    psv[1].mpw = pct(w * 100, 1);
    psv[1].mpl = pct(l * 100, 1);
    psv[1].mow = pct(1 / w, 2);
    psv[1].mol = pct(1 / l, 2);
    w = psv[1].stw / psv[1].mtp;
    l = psv[1].stl / psv[1].mtp;
    psv[1].scw = getColor(w);
    psv[1].scl = getColor(l);
    psv[1].spw = pct(w * 100, 1);
    psv[1].spl = pct(l * 100, 1);
    psv[1].sow = pct(1 / w, 2);
    psv[1].sol = pct(1 / l, 2);
}
function pct(v, n) {
    return Number(Math.round(v + 'e' + n) + 'e-' + n);
}
function getColor(value) {
    var hue = (value * 120).toString(10);
    return ["hsl(", hue, ",100%,65%)"].join("");
}
function visualize() {
    calc(0);
    calc(1);
    sv("sc0", psv[0].sc);
    sv("sc1", psv[1].sc);
    sv("mtw0", psv[0].mtw);
    ctv("mtw0", "green");
    sv("mtp0", psv[0].mtp);
    sv("mtl0", psv[0].mtl);
    ctv("mtl0", "red");
    sv("mtw1", psv[1].mtw);
    ctv("mtw1", "green");
    sv("mtp1", psv[1].mtp);
    sv("mtl1", psv[1].mtl);
    ctv("mtl1", "red");
    sv("stw0", psv[0].stw);
    ctv("stw0", "green");
    sv("stp0", psv[0].mtp);
    sv("stl0", psv[0].stl);
    ctv("stl0", "red");
    sv("stw1", psv[1].stw);
    ctv("stw1", "green");
    sv("stp1", psv[1].mtp);
    sv("stl1", psv[1].stl);
    ctv("stl1", "red");

    sv("mpw0", psv[0].mpw + "%");
    cv("mpw0", psv[0].mcw);
    sv("mpl0", psv[0].mpl + "%");
    cv("mpl0", psv[0].mcl);
    sv("spw0", psv[0].spw + "%");
    cv("spw0", psv[0].scw);
    sv("spl0", psv[0].spl + "%");
    cv("spl0", psv[0].scl);
    sv("mow0", psv[0].mow);
    cv("mow0", psv[0].mcw);
    sv("mol0", psv[0].mol);
    cv("mol0", psv[0].mcl);
    sv("sow0", psv[0].sow);
    cv("sow0", psv[0].scw);
    sv("sol0", psv[0].sol);
    cv("sol0", psv[0].scl);

    sv("mpw1", psv[1].mpw + "%");
    cv("mpw1", psv[1].mcw);
    sv("mpl1", psv[1].mpl + "%");
    cv("mpl1", psv[1].mcl);
    sv("spw1", psv[1].spw + "%");
    cv("spw1", psv[1].scw);
    sv("spl1", psv[1].spl + "%");
    cv("spl1", psv[1].scl);
    sv("mow1", psv[1].mow);
    cv("mow1", psv[1].mcw);
    sv("mol1", psv[1].mol);
    cv("mol1", psv[1].mcl);
    sv("sow1", psv[1].sow);
    cv("sow1", psv[1].scw);
    sv("sol1", psv[1].sol);
    cv("sol1", psv[1].scl);
}
function sv(n, v) {
    document.getElementById(n).innerHTML = v;
}
function cv(n, v) {
    document.getElementById(n).style.backgroundColor = v;
}
function ctv(n, v) {
    document.getElementById(n).style.color = v;
}
