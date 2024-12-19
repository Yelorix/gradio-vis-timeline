const {
  SvelteComponent: M,
  append_hydration: w,
  attr: S,
  children: k,
  claim_element: T,
  claim_text: I,
  detach: _,
  element: x,
  init: L,
  insert_hydration: R,
  noop: C,
  safe_not_equal: U,
  set_data: V,
  text: q,
  toggle_class: d
} = window.__gradio__svelte__internal;
function j(i) {
  let e, t, a = E(
    /*value*/
    i[0]
  ) + "", l;
  return {
    c() {
      e = x("div"), t = x("div"), l = q(a), this.h();
    },
    l(c) {
      e = T(c, "DIV", { class: !0 });
      var u = k(e);
      t = T(u, "DIV", { class: !0 });
      var s = k(t);
      l = I(s, a), s.forEach(_), u.forEach(_), this.h();
    },
    h() {
      S(t, "class", "example-content svelte-1rustph"), S(e, "class", "example-container svelte-1rustph"), d(
        e,
        "table",
        /*type*/
        i[1] === "table"
      ), d(
        e,
        "gallery",
        /*type*/
        i[1] === "gallery"
      ), d(
        e,
        "selected",
        /*selected*/
        i[2]
      );
    },
    m(c, u) {
      R(c, e, u), w(e, t), w(t, l);
    },
    p(c, [u]) {
      u & /*value*/
      1 && a !== (a = E(
        /*value*/
        c[0]
      ) + "") && V(l, a), u & /*type*/
      2 && d(
        e,
        "table",
        /*type*/
        c[1] === "table"
      ), u & /*type*/
      2 && d(
        e,
        "gallery",
        /*type*/
        c[1] === "gallery"
      ), u & /*selected*/
      4 && d(
        e,
        "selected",
        /*selected*/
        c[2]
      );
    },
    i: C,
    o: C,
    d(c) {
      c && _(e);
    }
  };
}
function E(i) {
  const e = i.items.length, t = i.groups.length, a = z(i.items);
  return `${i.description ? i.description : `${e} item${e !== 1 ? "s" : ""} in ${t} group${t !== 1 ? "s" : ""}`}
${a}`;
}
function z(i) {
  if (i.length === 0) return "";
  const e = i.flatMap((l) => [new Date(l.start), l.end ? new Date(l.end) : null]).filter((l) => l !== null), t = new Date(Math.min(...e.map((l) => l.getTime()))), a = new Date(Math.max(...e.map((l) => l.getTime())));
  return t.getTime() === a.getTime() ? f(t, !0) : `${f(t)} - ${f(a)}`;
}
function f(i, e = !1) {
  return e ? i.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric"
  }) : i.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric"
  });
}
function A(i, e, t) {
  let { value: a } = e, { type: l } = e, { selected: c = !1 } = e, { options: u = void 0 } = e, { preserve_old_content_on_value_change: s = void 0 } = e, { label: m = void 0 } = e, { interactive: r = void 0 } = e, { visible: o = void 0 } = e, { elem_id: g = void 0 } = e, { elem_classes: h = void 0 } = e, { key: v = void 0 } = e, { samples_dir: y = void 0 } = e, { index: b = void 0 } = e, { root: D = void 0 } = e;
  return i.$$set = (n) => {
    "value" in n && t(0, a = n.value), "type" in n && t(1, l = n.type), "selected" in n && t(2, c = n.selected), "options" in n && t(3, u = n.options), "preserve_old_content_on_value_change" in n && t(4, s = n.preserve_old_content_on_value_change), "label" in n && t(5, m = n.label), "interactive" in n && t(6, r = n.interactive), "visible" in n && t(7, o = n.visible), "elem_id" in n && t(8, g = n.elem_id), "elem_classes" in n && t(9, h = n.elem_classes), "key" in n && t(10, v = n.key), "samples_dir" in n && t(11, y = n.samples_dir), "index" in n && t(12, b = n.index), "root" in n && t(13, D = n.root);
  }, [
    a,
    l,
    c,
    u,
    s,
    m,
    r,
    o,
    g,
    h,
    v,
    y,
    b,
    D
  ];
}
class B extends M {
  constructor(e) {
    super(), L(this, e, A, j, U, {
      value: 0,
      type: 1,
      selected: 2,
      options: 3,
      preserve_old_content_on_value_change: 4,
      label: 5,
      interactive: 6,
      visible: 7,
      elem_id: 8,
      elem_classes: 9,
      key: 10,
      samples_dir: 11,
      index: 12,
      root: 13
    });
  }
}
export {
  B as default
};
