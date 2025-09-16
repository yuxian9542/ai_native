(function(a, c) {
    a.ue_mcm || a.ue.isBF || (a.ue_mcm = function() {
        function p(a) {
            if (a.id)
                return "//*[@id='" + a.id + "']";
            var c;
            c = 1;
            var e;
            for (e = a.previousSibling; e; e = e.previousSibling)
                e.nodeName == a.nodeName && (c += 1);
            e = a.nodeName;
            1 != c && (e += "[" + c + "]");
            a.parentNode && (e = p(a.parentNode) + "/" + e);
            return e
        }
        function l(a) {
            var e = a.srcElement || a.target || {}
              , l = {
                k: k,
                w: c.body.scrollWidth,
                h: c.body.scrollHeight,
                t: j(),
                x: a.pageX,
                y: a.pageY,
                p: p(e),
                n: e.nodeName,
                e: i
            };
            a.button && (l.b = a.button);
            e.href && (l.r = e.href);
            e.id && (l.i = e.id);
            e.className && (l.c = e.className.split(/\s+/));
            n(l, {
                n: 1,
                c: 1
            })
        }
        var k = "mcm", j, e = a.ue, n = a.ue_cel.log, i = a.ue_mce || "click";
        return {
            on: function(a) {
                j = a.ts;
                e.attach && e.attach(i, l, c)
            },
            off: function() {
                e.detach && e.detach(i, l, c)
            },
            ready: function() {
                return a.ue_cel && a.ue_cel.log
            },
            reset: function() {}
        }
    }(),
    a.ue_cel && a.ue_cel.registerModule("mouse click module", a.ue_mcm))
}
)(ue_csm, document);
(function(a, c) {
    a.ue_mmm || a.ue.isBF || (a.ue_mmm = function() {
        function p(a) {
            h = {
                x: a.pageX,
                y: a.pageY
            }
        }
        function l() {
            !h || t && h.x == t.x && h.y == t.y || k()
        }
        function k() {
            if (h) {
                var a = {
                    k: j,
                    t: e(),
                    x: h.x,
                    y: h.y
                };
                ue_cel.log(a);
                t = h
            }
        }
        var j = "mmm3", e, n, i = a.ue, g, h, t;
        return {
            on: function(a) {
                e = a.ts;
                n = a.ns;
                i.attach("mousemove", p, c);
                g = setInterval(l, 100)
            },
            off: function() {
                n && k();
                clearInterval(g);
                i.detach("mousemove", p, c)
            },
            ready: function() {
                return 1
            },
            reset: function() {
                t = h = null
            }
        }
    }(),
    a.ue_cel && a.ue_cel.registerModule("mouse move module", a.ue_mmm))
}
)(ue_csm, document);