System.register(
  "chunks:///_virtual/BackgroundView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./LoadUtils.ts",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
  ],
  function (t) {
    "use strict";
    var n, e, i, o, r, a, u, c, s, g, l, p, f, b, d, h;
    return {
      setters: [
        function (t) {
          (n = t.applyDecoratedDescriptor),
            (e = t.inheritsLoose),
            (i = t.initializerDefineProperty),
            (o = t.assertThisInitialized),
            (r = t.createClass);
        },
        function (t) {
          (a = t.cclegacy), (u = t._decorator), (c = t.sp), (s = t.Sprite);
        },
        function (t) {
          g = t.EBundles;
        },
        function (t) {
          l = t.LoadUtils;
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          f = t.inject;
        },
        function (t) {
          b = t.default;
        },
        function (t) {
          d = t.default;
        },
        function (t) {
          h = t.GameEvent;
        },
      ],
      execute: function () {
        var m, v, y, S, w, D, _, k, B, E, L, C, A;
        a._RF.push({}, "62286ZNjhxEsphH0ACSCQCb", "BackgroundView", void 0);
        var G = u.ccclass;
        u.property,
          t(
            "BackgroundView",
            ((m = G("BackgroundView")),
            (v = f("bgContent/bgLeft", s)),
            (y = f("bgContent/bgRight", s)),
            (S = f("bgDown", s)),
            (w = f("bgSpine", c.Skeleton)),
            (D = f("bgTopSpine", c.Skeleton)),
            m(
              ((B = n(
                (k = (function (t) {
                  function n() {
                    for (
                      var n, e = arguments.length, r = new Array(e), a = 0;
                      a < e;
                      a++
                    )
                      r[a] = arguments[a];
                    return (
                      (n = t.call.apply(t, [this].concat(r)) || this),
                      i(n, "bgLeft", B, o(n)),
                      i(n, "bgRight", E, o(n)),
                      i(n, "bgDown", L, o(n)),
                      i(n, "bgSpine", C, o(n)),
                      i(n, "bgTopSpine", A, o(n)),
                      n
                    );
                  }
                  e(n, t);
                  var a = n.prototype;
                  return (
                    (a.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (a.start = function () {
                      this.init();
                    }),
                    (a.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (a.init = function () {
                      b.useProEffect ||
                        ((this.bgSpine.node.active = !1),
                        (this.bgTopSpine.node.active = !1));
                    }),
                    (a.setBg = function (t) {
                      var n = b.getData().filePaths.common,
                        e = t ? "mg_bg" : "fg_bg",
                        i = t ? "mg_board" : "fg_board";
                      (this.bgLeft.spriteFrame = this.bgRight.spriteFrame =
                        l.getDirSp(g[g.g1001], n, e)),
                        this.bgDown &&
                          (this.bgDown.spriteFrame = l.getDirSp(
                            g[g.g1001],
                            n,
                            i
                          ));
                    }),
                    (a.setBgAnimation = function (t) {
                      var n = t ? "background_M" : "background_FG",
                        e = t ? "background_M_top" : "background_FG_top";
                      b.useProEffect &&
                        (this.bgSpine.setAnimation(0, n, !0),
                        this.bgTopSpine.setAnimation(0, e, !0));
                    }),
                    (a.reset = function () {}),
                    (a.setData = function (t) {}),
                    (a.show = function () {
                      this.node.active = !0;
                    }),
                    (a.hide = function () {
                      this.node.active = !1;
                    }),
                    (a.addEvents = function () {
                      var t = this;
                      this.on(h.CHANGE_GAME_STYLE, function (n) {
                        t.setBgAnimation(n.data), t.setBg(n.data);
                      });
                    }),
                    r(n, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(d);
                        },
                      },
                    ]),
                    n
                  );
                })(p)).prototype,
                "bgLeft",
                [v],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (E = n(k.prototype, "bgRight", [y], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (L = n(k.prototype, "bgDown", [S], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (C = n(k.prototype, "bgSpine", [w], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (A = n(k.prototype, "bgTopSpine", [D], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (_ = k))
            ) || _)
          );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/BigwinView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./UIView.ts",
    "./Decorators.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkEvent.ts",
    "./CmmSlotUtils.ts",
    "./MathUtil.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./ReplayModel.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var e,
      i,
      n,
      a,
      o,
      s,
      l,
      c,
      h,
      u,
      r,
      d,
      p,
      f,
      _,
      w,
      m,
      g,
      B,
      O,
      A,
      N,
      S,
      T,
      y,
      C,
      W,
      E,
      L;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (i = t.inheritsLoose),
            (n = t.initializerDefineProperty),
            (a = t.assertThisInitialized),
            (o = t.createClass);
        },
        function (t) {
          (s = t.cclegacy),
            (l = t._decorator),
            (c = t.sp),
            (h = t.Tween),
            (u = t.macro),
            (r = t.NodeEventType),
            (d = t.tween),
            (p = t.Vec3),
            (f = t.KeyCode),
            (_ = t.Node),
            (w = t.Label);
        },
        function (t) {
          m = t.default;
        },
        function (t) {
          g = t.inject;
        },
        function (t) {
          B = t.default;
        },
        function (t) {
          O = t.SlotFrameworkEvent;
        },
        function (t) {
          A = t.CmmSlotUtils;
        },
        function (t) {
          N = t.default;
        },
        function (t) {
          (S = t.EBTM), (T = t.default);
        },
        function (t) {
          y = t.default;
        },
        function (t) {
          C = t.GameEvent;
        },
        function (t) {
          W = t.EGameType;
        },
        function (t) {
          E = t.default;
        },
        function (t) {
          L = t.default;
        },
      ],
      execute: function () {
        var b, P, I, M, R, v, U, D, F, G, k, V, z, H, K;
        s._RF.push({}, "a74e4O3qV9BN4tXak+yb7nf", "BigwinView", void 0);
        var Y,
          Z = l.ccclass;
        l.property;
        !(function (t) {
          (t[(t.NONE = 0)] = "NONE"),
            (t[(t.SHOW_BIGWIN = 1)] = "SHOW_BIGWIN"),
            (t[(t.SHOW_BUGWIN_NUMBER = 2)] = "SHOW_BUGWIN_NUMBER"),
            (t[(t.SHOW_BUGWIN_NUMBER_END = 3)] = "SHOW_BUGWIN_NUMBER_END"),
            (t[(t.BIGWIN_COMPLETED = 4)] = "BIGWIN_COMPLETED");
        })(Y || (Y = {}));
        t(
          "BigwinView",
          ((b = Z("BigwinView")),
          (P = g("alert", _)),
          (I = g("alert/effectBg", c.Skeleton)),
          (M = g("alert/effectFont", c.Skeleton)),
          (R = g("alert/totalWin", w)),
          (v = g("alert/fireworks", c.Skeleton)),
          (U = g("alert/coinSprays", _)),
          b(
            ((G = e(
              (F = (function (t) {
                function e() {
                  for (
                    var e, i = arguments.length, o = new Array(i), s = 0;
                    s < i;
                    s++
                  )
                    o[s] = arguments[s];
                  return (
                    (e = t.call.apply(t, [this].concat(o)) || this),
                    n(e, "alert", G, a(e)),
                    n(e, "effectBg", k, a(e)),
                    n(e, "effectFont", V, a(e)),
                    n(e, "totalWin", z, a(e)),
                    n(e, "fireworks", H, a(e)),
                    n(e, "coinSprays", K, a(e)),
                    (e.bigwinFontFileNames = [
                      "w_big",
                      "w_super",
                      "w_mega",
                      "w_ultra",
                      "w_legend",
                    ]),
                    (e.completedCB = null),
                    (e.tweenNumTween = null),
                    (e.bigwinVO = null),
                    (e.playBigFontLoop = null),
                    (e.showWinStatus = Y.NONE),
                    (e.playPrizeLoopBtmSchedule = null),
                    (e.playPrizeVoiceBtmSchedule = null),
                    e
                  );
                }
                i(e, t);
                var s = e.prototype;
                return (
                  (s.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (s.start = function () {
                    this.init();
                  }),
                  (s.onDestroy = function () {
                    this.stopAllMusicAndSchedule(),
                      t.prototype.onDestroy.call(this);
                  }),
                  (e.getPrefabUrl = function () {
                    return "prefabs/" + L.getViewModeParam() + "/BigwinView";
                  }),
                  (s.init = function () {
                    this.enabledKeyDown = !0;
                  }),
                  (s.show = function (e) {
                    t.prototype.show.call(this), this.closeNodes();
                  }),
                  (s.onClose = function () {
                    this.unscheduleAllCallbacks(),
                      h.stopAllByTarget(this),
                      this.closeNodes(),
                      this.stopAllMusicAndSchedule(),
                      App.globalAudio.resumeMusic(),
                      this.close();
                  }),
                  (s.stopAllMusicAndSchedule = function () {
                    dispatch(C.STOP_BTM, { data: S.WIN_LOOP }),
                      dispatch(C.STOP_BTM, { data: S.SMALL_PRIZE_IN }),
                      dispatch(C.STOP_BTM, { data: S.ULTRA_IN }),
                      dispatch(C.STOP_BTM, { data: S.LEGEND_IN }),
                      dispatch(C.STOP_BTM, { data: S.S_PRIZE_LOOP }),
                      dispatch(C.STOP_BTM, { data: S.L_PRIZE_LOOP }),
                      dispatch(C.STOP_BTM, { data: S.FIREWORKS }),
                      dispatch(C.STOP_BTM, { data: S.BIG_VOCAL }),
                      dispatch(C.STOP_BTM, { data: S.SUPER_VOCAL }),
                      dispatch(C.STOP_BTM, { data: S.MEGA_VOCAL }),
                      dispatch(C.STOP_BTM, { data: S.ULTRA_VOCAL }),
                      dispatch(C.STOP_BTM, { data: S.LEGENDARY_VOCAL }),
                      this.unschedule(this.playPrizeLoopBtmSchedule),
                      this.unschedule(this.playPrizeVoiceBtmSchedule);
                  }),
                  (s.closeNodes = function () {
                    (this.effectBg.node.active = !1),
                      (this.effectFont.node.active = !1),
                      (this.totalWin.node.active = !1),
                      (this.fireworks.node.active = !1),
                      (this.coinSprays.active = !1),
                      this.coinSprays.children.forEach(function (t) {
                        t.active = !1;
                      }),
                      this.alert.targetOff(this),
                      T.stopOnBigwinPrize && (B.active = !1);
                  }),
                  (s.playAnimation = function (t, e) {
                    var i = this,
                      n = 0 != t,
                      a = t >= 4,
                      o = this.bigwinVO.isRoundWin,
                      s = 0;
                    App.globalAudio.pauseMusic(),
                      n && !o
                        ? a
                          ? (this.showFireworks(),
                            4 == t
                              ? (dispatch(C.PLAY_BTM, {
                                  data: { url: S.ULTRA_IN },
                                }),
                                (s = 2))
                              : 5 == t &&
                                (dispatch(C.PLAY_BTM, {
                                  data: { url: S.LEGEND_IN },
                                }),
                                (s = 2.5)),
                            this.scheduleOnce(function () {
                              i.playBigwin(t - 1, e);
                            }, s))
                          : this.playBigwin(t - 1, e)
                        : (this.playWin(e),
                          this.showCoinSpray(),
                          dispatch(C.PLAY_BTM, {
                            data: { url: S.WIN_LOOP, loop: !0 },
                          }));
                  }),
                  (s.playWin = function (t) {
                    var e = this,
                      i = T.getData().bigwinAutoCloseTime;
                    (this.effectBg.node.active = !0),
                      (this.effectFont.node.active = !0),
                      (this.effectFont.skeletonData =
                        this.data.getGameAlertSpine("w_win")),
                      this.effectFont.setAnimation(0, "in", !1),
                      this.effectFont.setCompleteListener(function () {
                        e.effectFont.setAnimation(0, "loop", !1),
                          (e.playBigFontLoop = function () {
                            e.effectFont.setAnimation(0, "loop", !1);
                          }),
                          e.schedule(
                            e.playBigFontLoop,
                            2.5,
                            u.REPEAT_FOREVER,
                            0
                          ),
                          e.effectFont.setCompleteListener(null);
                      }),
                      (this.effectBg.skeletonData =
                        this.data.getGameAlertSpine("w_win_bg")),
                      this.effectBg.setAnimation(0, "in", !1),
                      this.effectBg.setCompleteListener(function () {
                        e.effectBg.setAnimation(0, "loop", !0);
                      }),
                      this.scheduleOnce(this.showWinResult, i + t);
                  }),
                  (s.playBigwin = function (t, e) {
                    var i = this,
                      n = T.getData().bigwinAutoCloseTime,
                      a = this.bigwinFontFileNames[t],
                      o =
                        (this.data.getData().parser.bigwinReach.level,
                        this.bigwinVO.isFgOut),
                      s = 2.5;
                    3 == t ? (s = 2.3) : 4 == t && (s = 2),
                      (this.effectBg.node.active = !0),
                      (this.effectFont.node.active = !0),
                      (this.effectFont.skeletonData =
                        this.data.getGameAlertSpine(a)),
                      this.effectFont.setAnimation(0, "in", !1),
                      this.effectFont.setCompleteListener(function () {
                        i.effectFont.setAnimation(0, "loop", !1),
                          (i.playBigFontLoop = function () {
                            i.effectFont.setAnimation(0, "loop", !1);
                          }),
                          i.schedule(
                            i.playBigFontLoop,
                            2.5,
                            u.REPEAT_FOREVER,
                            0
                          ),
                          i.effectFont.setCompleteListener(null);
                      }),
                      (this.effectBg.skeletonData = this.data.getGameAlertSpine(
                        a + "_bg"
                      )),
                      this.effectBg.setAnimation(0, "in", !1),
                      this.effectBg.setCompleteListener(function () {
                        i.effectBg.setAnimation(0, "loop", !0);
                      }),
                      t < 3 &&
                        dispatch(C.PLAY_BTM, {
                          data: { url: S.SMALL_PRIZE_IN },
                        }),
                      this.playWinBtm(t),
                      (this.playPrizeLoopBtmSchedule = function () {
                        var e = t < 3 ? S.S_PRIZE_LOOP : S.L_PRIZE_LOOP;
                        i.showCoinSpray(),
                          dispatch(C.PLAY_BTM, { data: { url: e, loop: !0 } });
                      }),
                      this.scheduleOnce(this.playPrizeLoopBtmSchedule, s),
                      n &&
                        !o &&
                        this.scheduleOnce(this.showWinResult, n + s + e),
                      E.isReplay
                        ? o
                          ? this.scheduleOnce(this.showWinResult, n + s + e)
                          : this.scheduleOnce(
                              this.addClickAlertCompleteCb,
                              e + s
                            )
                        : o
                        ? this.scheduleOnce(function () {
                            i.alert.once(
                              r.TOUCH_END,
                              function () {
                                return i.showWinResult();
                              },
                              n + s + e
                            );
                          }, n + s + e)
                        : this.scheduleOnce(
                            this.addClickAlertCompleteCb,
                            e + s
                          );
                  }),
                  (s.addClickAlertCompleteCb = function () {
                    this.alert.once(r.TOUCH_END, this.completedCB);
                    var t = T.getData().bigwinAutoCloseTime;
                    this.scheduleOnce(this.completedCB, t),
                      this.unschedule(this.addClickAlertCompleteCb);
                  }),
                  (s.playWinBtm = function (t) {
                    var e,
                      i = 0;
                    switch (t) {
                      case 0:
                        (e = S.BIG_VOCAL), (i = 1.2);
                        break;
                      case 1:
                        (e = S.SUPER_VOCAL), (i = 0.8);
                        break;
                      case 2:
                        (e = S.MEGA_VOCAL), (i = 0.9);
                        break;
                      case 3:
                        (e = S.ULTRA_VOCAL), (i = 0.9);
                        break;
                      case 4:
                        (e = S.LEGENDARY_VOCAL), (i = 0);
                    }
                    (this.playPrizeVoiceBtmSchedule = function () {
                      dispatch(C.PLAY_BTM, { data: { url: e } });
                    }),
                      this.scheduleOnce(this.playPrizeVoiceBtmSchedule, i);
                  }),
                  (s.playBounceTween = function (t, e) {
                    d(t)
                      .to(0.1, { scale: new p(1.8, 1.8, 1.8) })
                      .delay(0.01)
                      .to(
                        0.1,
                        { scale: new p(1, 1, 1) },
                        {
                          onComplete: function () {
                            e && e();
                          },
                        }
                      )
                      .start();
                  }),
                  (s.showFireworks = function () {
                    (this.fireworks.node.active = !0),
                      this.fireworks.setAnimation(0, "fireworks", !0),
                      (this.fireworks.timeScale = 1.5);
                  }),
                  (s.showCoinSpray = function () {
                    var t = this,
                      e = this.coinSprays.getComponentsInChildren(c.Skeleton);
                    this.coinSprays.active = !0;
                    for (
                      var i = function () {
                          var i = e[n];
                          0 == n
                            ? ((i.node.active = !0),
                              i.setAnimation(0, "coin_01", !1))
                            : 1 == n
                            ? t.scheduleOnce(function () {
                                (i.node.active = !0),
                                  i.setAnimation(0, "coin_02", !1);
                              }, 1.3)
                            : t.scheduleOnce(function () {
                                var t = N.getRandomNumber(3, 6);
                                (i.node.active = !0),
                                  i.setAnimation(0, "radom_0" + t, !1),
                                  i.setCompleteListener(function () {
                                    var t = N.getRandomNumber(3, 6);
                                    i.setAnimation(0, "radom_0" + t, !1);
                                  });
                              }, 2.8 + 0.5 * (n - 2));
                        },
                        n = 0;
                      n < e.length;
                      n++
                    )
                      i();
                  }),
                  (s.showWinResult = function () {
                    var t = this,
                      e = this.data.getData().gameState,
                      i = e.totalWinnings,
                      n = e.roundWinnings,
                      a = this.data.currentGameType == W.MAIN_GAME,
                      o =
                        (this.data.getData().parser.bigwinReach.level,
                        this.bigwinVO.isFgOut);
                    this.tweenNumTween && this.tweenNumTween.stop(),
                      (this.totalWin.string = A.formatNumber(
                        this.bigwinVO.winnings
                      )),
                      this.playBounceTween(this.totalWin.node),
                      this.unschedule(this.playBigFontLoop),
                      dispatch(C.QUICK_STOP_TOTAL_WINNINGS, { data: i }),
                      dispatch(C.QUICK_STOP_WIN_AMOUNT, { data: a ? i : n }),
                      this.unschedule(this.showWinResult),
                      (this.showWinStatus = Y.SHOW_BUGWIN_NUMBER_END),
                      this.bigwinVO.isRoundWin
                        ? this.scheduleOnce(this.completedCB, 1)
                        : o
                        ? E.isReplay
                          ? (this.stopAllMusicAndSchedule(), this.completedCB())
                          : this.scheduleOnce(function () {
                              t.alert.once(r.TOUCH_END, function () {
                                t.stopAllMusicAndSchedule(), t.completedCB();
                              });
                            }, 1)
                        : this.addClickAlertCompleteCb();
                  }),
                  (s.showBigwin = function (t, e) {
                    var i = this,
                      n = this.data.getData().gameState,
                      a = n.totalWinnings,
                      o = n.roundWinnings,
                      s = this.data.currentGameType == W.MAIN_GAME,
                      l = this.data.getData().definition.digital,
                      c = this.data.getData().parser.bigwinReach.level,
                      h = e.winnings,
                      u = e.isRoundWin,
                      d = 5 + 3 * c,
                      p = c >= 4 && !u ? 4.5 : 2.7,
                      f = {
                        label: this.totalWin,
                        start: 0,
                        end: h,
                        tweenTime: d,
                        digital: l,
                        useThousandsSeparator: !0,
                      };
                    (u || 0 == c) && (p = 0),
                      (this.bigwinVO = e),
                      (this.showWinStatus = Y.SHOW_BIGWIN),
                      (this.completedCB = function () {
                        i.unscheduleAllCallbacks(),
                          (i.showWinStatus = Y.BIGWIN_COMPLETED),
                          i.tweenNumTween && i.tweenNumTween.stop(),
                          dispatch(C.QUICK_STOP_TOTAL_WINNINGS, { data: a }),
                          dispatch(C.QUICK_STOP_WIN_AMOUNT, {
                            data: s ? a : o,
                          }),
                          t(),
                          i.onClose(),
                          i.unschedule(i.playBigFontLoop);
                      }),
                      this.playAnimation(c, d),
                      this.scheduleOnce(function () {
                        (i.showWinStatus = Y.SHOW_BUGWIN_NUMBER),
                          (i.totalWin.node.active = !0),
                          (i.tweenNumTween = A.tweenNum(f)),
                          i.alert.once(
                            r.TOUCH_END,
                            function () {
                              i.showWinResult();
                            },
                            i
                          ),
                          dispatch(O.UPDATE_TOTAL_WINNINGS, {
                            data: { value: a, tweenTime: d },
                          }),
                          dispatch(C.UPDATE_WIN_AMOUNT, {
                            data: { value: h, tweenTime: d },
                          });
                      }, p);
                  }),
                  (s.onKeyDown = function (e) {
                    if (
                      (t.prototype.onKeyDown.call(this, e),
                      e.keyCode === f.SPACE)
                    )
                      switch (this.showWinStatus) {
                        case Y.SHOW_BUGWIN_NUMBER:
                          this.showWinResult(),
                            (this.showWinStatus = Y.SHOW_BUGWIN_NUMBER_END);
                          break;
                        case Y.SHOW_BUGWIN_NUMBER_END:
                          (this.showWinStatus = Y.BIGWIN_COMPLETED),
                            this.scheduleOnce(this.completedCB, 0.5);
                      }
                  }),
                  (s.addEvents = function () {}),
                  o(e, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(y);
                      },
                    },
                  ]),
                  e
                );
              })(m)).prototype,
              "alert",
              [P],
              {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              }
            )),
            (k = e(F.prototype, "effectBg", [I], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (V = e(F.prototype, "effectFont", [M], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (z = e(F.prototype, "totalWin", [R], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (H = e(F.prototype, "fireworks", [v], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (K = e(F.prototype, "coinSprays", [U], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (D = F))
          ) || D)
        );
        s._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/BuyFeatureButton.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./SlotFrameworkEvent.ts",
    "./type2.ts",
    "./CmmSlotUtils.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
  ],
  function (t) {
    "use strict";
    var e, n, i, o, a, r, u, s, c, l, f, h, d, p, y, B, E, S, b, v, F;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (n = t.inheritsLoose),
            (i = t.initializerDefineProperty),
            (o = t.assertThisInitialized),
            (a = t.createClass);
        },
        function (t) {
          (r = t.cclegacy),
            (u = t._decorator),
            (s = t.Button),
            (c = t.NodeEventType),
            (l = t.v3),
            (f = t.Color),
            (h = t.Label),
            (d = t.Sprite);
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          y = t.inject;
        },
        function (t) {
          B = t.SlotFrameworkEvent;
        },
        function (t) {
          E = t.ESpinStatus;
        },
        function (t) {
          S = t.CmmSlotUtils;
        },
        function (t) {
          b = t.EBTM;
        },
        function (t) {
          v = t.default;
        },
        function (t) {
          F = t.GameEvent;
        },
      ],
      execute: function () {
        var T, _, m, C, A, g, U;
        r._RF.push({}, "adeb2bKLWhLeobwXKP7qvfi", "BuyFeatureButton", void 0);
        var D = u.ccclass;
        u.property,
          t(
            "BuyFeatureButton",
            ((T = D("BuyFeatureButton")),
            (_ = y("stake", h)),
            (m = y("font", d)),
            T(
              ((g = e(
                (A = (function (t) {
                  function e() {
                    for (
                      var e, n = arguments.length, a = new Array(n), r = 0;
                      r < n;
                      r++
                    )
                      a[r] = arguments[r];
                    return (
                      (e = t.call.apply(t, [this].concat(a)) || this),
                      i(e, "stake", g, o(e)),
                      i(e, "fontSprite", U, o(e)),
                      (e.button = null),
                      e
                    );
                  }
                  n(e, t);
                  var r = e.prototype;
                  return (
                    (r.onLoad = function () {
                      t.prototype.onLoad.call(this), this.init();
                    }),
                    (r.start = function () {}),
                    (r.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (r.init = function () {
                      (this.button = this.node.getComponent(s)),
                        this.node.on(
                          c.TOUCH_START,
                          this.buyFeatureBtnHandler,
                          this
                        ),
                        this.node.on(
                          c.TOUCH_MOVE,
                          this.buyFeatureBtnHandler,
                          this
                        ),
                        this.node.on(
                          c.TOUCH_CANCEL,
                          this.buyFeatureBtnHandler,
                          this
                        ),
                        this.node.on(
                          c.TOUCH_END,
                          this.buyFeatureBtnHandler,
                          this
                        ),
                        (this.fontSprite.spriteFrame =
                          this.data.getLocaleSpriteFrame("mg_btn_font"));
                    }),
                    (r.setBuyFeatureBtnActive = function (t) {
                      this.node.active = t;
                    }),
                    (r.buyFeatureBtnHandler = function (t) {
                      if (this.button.interactable) {
                        var e =
                          t.type == c.TOUCH_START
                            ? l(0.95, 0.95, 0.95)
                            : l(1, 1, 1);
                        this.node.children.forEach(function (t) {
                          t.setScale(e);
                        }),
                          t.type == c.TOUCH_END &&
                            (dispatch(F.OPEN_FEATURE_POPUP),
                            dispatch(F.PLAY_BTM, {
                              data: { url: b.OPEN_FEATURE },
                            }));
                      }
                    }),
                    (r.updateBuyFeatureStake = function (t) {
                      var e =
                        t *
                        this.data.getData().definition.buyFeature[0]
                          .featureRate;
                      this.stake.string = S.formatNumber(e);
                    }),
                    (r.updateBuyFeatureBtnStatus = function (t) {
                      var e = E.SPINING === t,
                        n = new f(255, 255, 255, 255),
                        i = new f(130, 130, 130, 255);
                      (this.button.interactable = !e),
                        (this.fontSprite.color = e ? i : n),
                        (this.stake.color = e ? i : n);
                    }),
                    (r.reset = function () {}),
                    (r.setData = function (t) {}),
                    (r.show = function () {
                      this.node.active = !0;
                    }),
                    (r.hide = function () {
                      this.node.active = !1;
                    }),
                    (r.addEvents = function () {
                      var t = this;
                      this.on(F.CHANGE_GAME_STYLE, function (e) {
                        t.setBuyFeatureBtnActive(e.data);
                      }),
                        this.on(B.UPDATE_STAKE, function (e) {
                          t.updateBuyFeatureStake(e.data);
                        }),
                        this.on(B.UPDATE_SPIN_STATUS, function (e) {
                          t.updateBuyFeatureBtnStatus(e.data);
                        });
                    }),
                    a(e, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(v);
                        },
                      },
                    ]),
                    e
                  );
                })(p)).prototype,
                "stake",
                [_],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (U = e(A.prototype, "fontSprite", [m], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (C = A))
            ) || C)
          );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/BuyFeatureView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Decorators.ts",
    "./StakeModel.ts",
    "./SlotFrameworkEvent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./Bundles.ts",
    "./LoadUtils.ts",
    "./UIView.ts",
    "./ObjectUtils.ts",
    "./GameSender.ts",
    "./DefinitionModel.ts",
    "./PlatformModel.ts",
    "./SettingsModel.ts",
    "./CmmSlotUtils.ts",
    "./MathUtil.ts",
    "./type2.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var e,
      n,
      i,
      a,
      o,
      r,
      l,
      s,
      u,
      c,
      p,
      f,
      d,
      h,
      m,
      g,
      B,
      b,
      S,
      y,
      F,
      T,
      C,
      E,
      v,
      U,
      k,
      _,
      w,
      A,
      D,
      O,
      H,
      I;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (n = t.inheritsLoose),
            (i = t.initializerDefineProperty),
            (a = t.assertThisInitialized),
            (o = t.createClass);
        },
        function (t) {
          (r = t.cclegacy),
            (l = t._decorator),
            (s = t.sp),
            (u = t.NodeEventType),
            (c = t.v3),
            (p = t.Button),
            (f = t.tween),
            (d = t.Sprite),
            (h = t.Node),
            (m = t.Label);
        },
        function (t) {
          g = t.inject;
        },
        function (t) {
          B = t.default;
        },
        function (t) {
          b = t.SlotFrameworkEvent;
        },
        function (t) {
          (S = t.EBTM), (y = t.default);
        },
        function (t) {
          F = t.default;
        },
        function (t) {
          T = t.GameEvent;
        },
        function (t) {
          C = t.EBundles;
        },
        function (t) {
          E = t.LoadUtils;
        },
        function (t) {
          v = t.default;
        },
        function (t) {
          U = t.ObjectUtils;
        },
        function (t) {
          k = t.GameSender;
        },
        function (t) {
          _ = t.default;
        },
        function (t) {
          w = t.default;
        },
        function (t) {
          A = t.default;
        },
        function (t) {
          D = t.CmmSlotUtils;
        },
        function (t) {
          O = t.default;
        },
        function (t) {
          H = t.ESpinStatus;
        },
        function (t) {
          I = t.default;
        },
      ],
      execute: function () {
        var L, P, x, V, M, R, N, z, j, G, Y, q, J, K, W, Z, Q, X, $;
        r._RF.push({}, "b43e1eAZwtDPYYC1opJ5eoL", "BuyFeatureView", void 0);
        var tt = l.ccclass;
        l.property,
          t(
            "BuyFeatureView",
            ((L = tt("BuyFeatureView")),
            (P = g("popup", h)),
            (x = g("popup/spines", h)),
            (V = g("popup/titleFont", h)),
            (M = g("popup/cancelBtn", h)),
            (R = g("popup/cancelBtn/fontSprite", d)),
            (N = g("popup/confirmBtn", h)),
            (z = g("popup/confirmBtn/fontSprite", d)),
            (j = g("popup/stake", m)),
            L(
              ((q = e(
                (Y = (function (t) {
                  function e() {
                    for (
                      var e, n = arguments.length, o = new Array(n), r = 0;
                      r < n;
                      r++
                    )
                      o[r] = arguments[r];
                    return (
                      (e = t.call.apply(t, [this].concat(o)) || this),
                      i(e, "popup", q, a(e)),
                      i(e, "spines", J, a(e)),
                      i(e, "titleFont", K, a(e)),
                      i(e, "cancelBtn", W, a(e)),
                      i(e, "cancelBtnFontSprite", Z, a(e)),
                      i(e, "confirmBtn", Q, a(e)),
                      i(e, "confirmFontSprite", X, a(e)),
                      i(e, "stake", $, a(e)),
                      (e.skeletons = []),
                      (e.titleFontTween = null),
                      e
                    );
                  }
                  n(e, t);
                  var r = e.prototype;
                  return (
                    (r.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (r.start = function () {
                      this.init();
                    }),
                    (r.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (e.getPrefabUrl = function () {
                      return (
                        "prefabs/" + I.getViewModeParam() + "/BuyFeatureView"
                      );
                    }),
                    (r.init = function () {
                      (this.skeletons = this.spines.getComponentsInChildren(
                        s.Skeleton
                      )),
                        this.createTitleFontLoopAnim(),
                        this.setData();
                    }),
                    (r.cancelBtnHandler = function (t) {
                      var e =
                        t.type == u.TOUCH_START
                          ? c(1.15, 1.15, 1.15)
                          : c(1.2, 1.2, 1.2);
                      this.cancelBtn.children.forEach(function (t) {
                        t.setScale(e);
                      }),
                        t.type == u.TOUCH_END && this.closePopup();
                    }),
                    (r.confirmBtnHandler = function (t) {
                      var e =
                        t.type == u.TOUCH_START
                          ? c(1.15, 1.15, 1.15)
                          : c(1.2, 1.2, 1.2);
                      this.confirmBtn.children.forEach(function (t) {
                        t.setScale(e);
                      }),
                        t.type == u.TOUCH_END && this.sendFeatureReq();
                    }),
                    (r.closePopup = function () {
                      App.uiManager.close(e),
                        dispatch(T.PLAY_BTM, {
                          data: { url: S.CLOSE_FEATURE },
                        });
                    }),
                    (r.addButtonsEvent = function () {
                      this.cancelBtn.on(
                        u.TOUCH_START,
                        this.cancelBtnHandler,
                        this
                      ),
                        this.cancelBtn.on(
                          u.TOUCH_MOVE,
                          this.cancelBtnHandler,
                          this
                        ),
                        this.cancelBtn.on(
                          u.TOUCH_CANCEL,
                          this.cancelBtnHandler,
                          this
                        ),
                        this.cancelBtn.on(
                          u.TOUCH_END,
                          this.cancelBtnHandler,
                          this
                        ),
                        this.confirmBtn.on(
                          u.TOUCH_START,
                          this.confirmBtnHandler,
                          this
                        ),
                        this.confirmBtn.on(
                          u.TOUCH_MOVE,
                          this.confirmBtnHandler,
                          this
                        ),
                        this.confirmBtn.on(
                          u.TOUCH_CANCEL,
                          this.confirmBtnHandler,
                          this
                        ),
                        this.confirmBtn.on(
                          u.TOUCH_END,
                          this.confirmBtnHandler,
                          this
                        );
                    }),
                    (r.sendFeatureReq = function () {
                      var t = {
                        ratioIndex: B.ratioIndex,
                        ratioValue: B.ratioValue,
                        stakeIndex: B.stakeIndex,
                        stakeValue: B.stakeValue,
                      };
                      if (0 === w.getData().player.balance.amount) {
                        var e = {
                            text: App.getLanguage(
                              "insufficientFundError",
                              [],
                              C[C.wrapper]
                            ),
                            confirmCb: function () {
                              n();
                            },
                            bbrCb: function () {
                              n();
                            },
                          },
                          n = function () {
                            dispatch(b.SHOW_AUTO_SPIN, { data: !0 }),
                              dispatch(b.UPDATE_SPIN_STATUS, { data: H.IDLE });
                          };
                        return (
                          (this.data.isOpenEarlyFlag = !1),
                          (this.data.isSendOutEarlyFlag = !1),
                          void App.gameAlert.show(e)
                        );
                      }
                      if (this.checkBalance(t))
                        App.senderManager
                          .get(k)
                          .buyFeature(t, this.needUpdateStake()),
                          this.setInteractable(!1),
                          this.cancelBtn.targetOff(this),
                          this.confirmBtn.targetOff(this);
                      else {
                        var i = {
                          text: App.getLanguage(
                            "insufficientFund",
                            [],
                            C[C.wrapper]
                          ),
                          confirmCb: function () {},
                          bbrCb: function () {},
                        };
                        App.gameAlert.show(i);
                      }
                    }),
                    (r.checkBalance = function (t) {
                      var e = _.getData().winlineDefs.length,
                        n = this.data.getData().definition.buyFeature,
                        i = t.stakeValue,
                        a = t.ratioValue,
                        o = O.multiply(a, i, e) * n[0].featureRate;
                      return w.getData().player.balance.amount - o >= 0;
                    }),
                    (r.updateBuyFeatureStake = function () {
                      var t =
                        B.getData().totalStake *
                        this.data.getData().definition.buyFeature[0]
                          .featureRate;
                      this.stake.string = D.formatNumber(t);
                    }),
                    (r.setInteractable = function (t) {
                      (this.confirmBtn.getComponent(p).interactable = t),
                        (this.cancelBtn.getComponent(p).interactable = t);
                    }),
                    (r.createTitleFontLoopAnim = function () {
                      this.titleFontTween = f(this.titleFont).repeatForever(
                        f()
                          .to(1.5, { scale: c(0.97, 0.97) })
                          .to(1.5, { scale: c(1, 1) })
                      );
                    }),
                    (r.needUpdateStake = function () {
                      var t = {
                          stakeIndex: A.stakeIndex,
                          ratioIndex: A.ratioIndex,
                        },
                        e = {
                          stakeIndex: B.stakeIndex,
                          ratioIndex: B.ratioIndex,
                        },
                        n = U.diffObjects(t, e);
                      return Object.keys(n).length > 0;
                    }),
                    (r.reset = function () {}),
                    (r.setData = function () {
                      var t = y.getData().filePaths.localeSpriteFrame;
                      (this.confirmFontSprite.spriteFrame = E.getDirSp(
                        C[C.g1001],
                        t,
                        "popup_font_01"
                      )),
                        (this.cancelBtnFontSprite.spriteFrame = E.getDirSp(
                          C[C.g1001],
                          t,
                          "popup_font_02"
                        )),
                        (this.titleFont.getComponent(d).spriteFrame =
                          E.getDirSp(C[C.g1001], t, "popup_font_03"));
                    }),
                    (r.openPopup = function () {
                      var t;
                      this.updateBuyFeatureStake(),
                        (this.popup.active = !0),
                        this.skeletons.forEach(function (t) {
                          t.setAnimation(0, "popup", !1),
                            t.setCompleteListener(function () {
                              t.setAnimation(0, "loop", !0),
                                t.setCompleteListener(null);
                            });
                        }),
                        this.setInteractable(!0),
                        this.addButtonsEvent(),
                        null == (t = this.titleFontTween) || t.start();
                    }),
                    (r.show = function () {
                      this.node.active = !0;
                    }),
                    (r.hide = function () {
                      this.node.active = !1;
                    }),
                    (r.addEvents = function () {
                      var t = this;
                      this.on(T.CLOSE_FEATURE_POPUP, function (e) {
                        t.closePopup();
                      }),
                        this.on(b.UPDATE_STAKE, function (e) {
                          t.updateBuyFeatureStake();
                        });
                    }),
                    o(e, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(F);
                        },
                      },
                    ]),
                    e
                  );
                })(v)).prototype,
                "popup",
                [P],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (J = e(Y.prototype, "spines", [x], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (K = e(Y.prototype, "titleFont", [V], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (W = e(Y.prototype, "cancelBtn", [M], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (Z = e(Y.prototype, "cancelBtnFontSprite", [R], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (Q = e(Y.prototype, "confirmBtn", [N], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (X = e(Y.prototype, "confirmFontSprite", [z], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              ($ = e(Y.prototype, "stake", [j], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (G = Y))
            ) || G)
          );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CharacterView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
  ],
  function (e) {
    "use strict";
    var t, n, i, a, r, o, c, f, l, s, m, u, p, h;
    return {
      setters: [
        function (e) {
          (t = e.applyDecoratedDescriptor),
            (n = e.inheritsLoose),
            (i = e.initializerDefineProperty),
            (a = e.assertThisInitialized),
            (r = e.createClass);
        },
        function (e) {
          (o = e.cclegacy), (c = e._decorator), (f = e.sp);
        },
        function (e) {
          l = e.default;
        },
        function (e) {
          s = e.inject;
        },
        function (e) {
          (m = e.default), (u = e.EBTM);
        },
        function (e) {
          p = e.default;
        },
        function (e) {
          h = e.GameEvent;
        },
      ],
      execute: function () {
        var w, E, d, b, g, F, v, y, C, S, A, _, L, D, R, T, k, z, M;
        o._RF.push({}, "b2c54+uI4REKZ4cawA79Jrx", "CharacterView", void 0);
        var N = c.ccclass;
        c.property,
          e(
            "CharacterView",
            ((w = N("CharacterView")),
            (E = s("manElement/man", f.Skeleton)),
            (d = s("womanElement/woman", f.Skeleton)),
            (b = s("manElement/lower", f.Skeleton)),
            (g = s("manElement/upper", f.Skeleton)),
            (F = s("manElement/fire", f.Skeleton)),
            (v = s("womanElement/lower", f.Skeleton)),
            (y = s("womanElement/upper", f.Skeleton)),
            (C = s("womanElement/fire", f.Skeleton)),
            w(
              ((_ = t(
                (A = (function (e) {
                  function t() {
                    for (
                      var t, n = arguments.length, r = new Array(n), o = 0;
                      o < n;
                      o++
                    )
                      r[o] = arguments[o];
                    return (
                      (t = e.call.apply(e, [this].concat(r)) || this),
                      i(t, "man", _, a(t)),
                      i(t, "woman", L, a(t)),
                      i(t, "manLowerEffect", D, a(t)),
                      i(t, "manUpperEffect", R, a(t)),
                      i(t, "manFireEffect", T, a(t)),
                      i(t, "womanLowerEffect", k, a(t)),
                      i(t, "womanUpperEffect", z, a(t)),
                      i(t, "womanFireEffect", M, a(t)),
                      (t.fgEffectNodes = []),
                      t
                    );
                  }
                  n(t, e);
                  var o = t.prototype;
                  return (
                    (o.onLoad = function () {
                      e.prototype.onLoad.call(this);
                    }),
                    (o.start = function () {
                      this.init();
                    }),
                    (o.onDestroy = function () {
                      e.prototype.onDestroy.call(this);
                    }),
                    (o.init = function () {
                      (this.fgEffectNodes = [
                        this.manLowerEffect.node,
                        this.manUpperEffect.node,
                        this.womanLowerEffect.node,
                        this.womanUpperEffect.node,
                      ]),
                        m.useProEffect ||
                          ((this.manLowerEffect.node.active = !1),
                          (this.womanLowerEffect.node.active = !1));
                    }),
                    (o.playCharacterManFire = function (e) {
                      var t = this;
                      this.man.setAnimation(0, "characterB_fire", !1),
                        (this.man.timeScale = e),
                        this.man.setCompleteListener(function () {
                          (t.man.timeScale = 1),
                            t.man.setAnimation(0, "characterB_idle", !0);
                        }),
                        dispatch(h.PLAY_BTM, {
                          data: { url: u.CH_MAN_TRANSITION },
                        }),
                        (this.manFireEffect.node.active = !0),
                        this.manFireEffect.setAnimation(0, "fireball", !1),
                        this.manFireEffect.setCompleteListener(function () {
                          t.manFireEffect.node.active = !1;
                        });
                    }),
                    (o.playCharacterWomanFire = function (e) {
                      var t = this;
                      this.woman.setAnimation(0, "characterA_fire", !1),
                        (this.woman.timeScale = e),
                        this.woman.setCompleteListener(function () {
                          (t.woman.timeScale = 1),
                            t.woman.setAnimation(0, "characterA_idle", !0);
                        }),
                        dispatch(h.PLAY_BTM, {
                          data: { url: u.CH_WOMAN_TRANSITION },
                        }),
                        (this.womanFireEffect.node.active = !0),
                        this.womanFireEffect.setAnimation(0, "fireball", !1),
                        this.womanFireEffect.setCompleteListener(function () {
                          t.womanFireEffect.node.active = !1;
                        });
                    }),
                    (o.showOpenFire = function () {
                      var e = m.getData().reelConfig.characterFireSpeed,
                        t = this.data.getData().parser.newTimesSymbols,
                        n = !1,
                        i = !1;
                      if (t.length) {
                        for (var a = 0; a < t.length; a++)
                          t[a].isRare ? (n = !0) : (i = !0);
                        i && this.playCharacterManFire(e),
                          n && this.playCharacterWomanFire(e);
                      }
                    }),
                    (o.speedUpCharacterFire = function () {
                      m.getData().reelConfig.characterFireSpeed;
                      var e = this.data.getData().parser.newTimesSymbols,
                        t = !1,
                        n = !1;
                      if (e.length) {
                        for (var i = 0; i < e.length; i++)
                          e[i].isRare ? (t = !0) : (n = !0);
                        n && (this.man.timeScale = 1.2 * this.man.timeScale),
                          t &&
                            (this.woman.timeScale = 1.2 * this.woman.timeScale);
                      }
                    }),
                    (o.setFgElements = function (e) {
                      this.fgEffectNodes.forEach(function (t) {
                        (m.useProEffect || "lower" !== t.name) &&
                          (t.active = !e);
                      });
                    }),
                    (o.reset = function () {}),
                    (o.setData = function (e) {}),
                    (o.show = function () {
                      this.node.active = !0;
                    }),
                    (o.hide = function () {
                      this.node.active = !1;
                    }),
                    (o.addEvents = function () {
                      var e = this;
                      this.on(h.SHOW_CHARACTER_FIRE, function (t) {
                        e.showOpenFire();
                      }),
                        this.on(h.SPEED_CHARACTER_FIRE_UP, function (t) {
                          e.speedUpCharacterFire();
                        }),
                        this.on(h.CHANGE_GAME_STYLE, function (t) {
                          e.setFgElements(t.data);
                        });
                    }),
                    r(t, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(p);
                        },
                      },
                    ]),
                    t
                  );
                })(l)).prototype,
                "man",
                [E],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (L = t(A.prototype, "woman", [d], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (D = t(A.prototype, "manLowerEffect", [b], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (R = t(A.prototype, "manUpperEffect", [g], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (T = t(A.prototype, "manFireEffect", [F], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (k = t(A.prototype, "womanLowerEffect", [v], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (z = t(A.prototype, "womanUpperEffect", [y], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (M = t(A.prototype, "womanFireEffect", [C], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (S = A))
            ) || S)
          );
        o._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateNewCloseSpinFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkEvent.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, o, i, s, r, l, u;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          o = e.FlowTrigger;
        },
        function (e) {
          i = e.SingletonExtends;
        },
        function (e) {
          s = e.SlotFrameworkEvent;
        },
        function (e) {
          r = e.default;
        },
        function (e) {
          l = e.GameEvent;
        },
        function (e) {
          u = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "a2e4cdeyshCPqF9jCh/8CFY",
          "CreateNewCloseSpinFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var i = a.prototype;
            return (
              (i.execute = function () {
                var e = this.createFlow();
                App.flowManager.registerFlow(e);
              }),
              (i.createFlow = function () {
                var e = new App.flowManager.Flow(u.CLOSE_SPIN_FLOW),
                  t = this.data.getData().gameState,
                  n = t.totalWinnings,
                  a = t.isJp,
                  i = t.noWinReward,
                  r = this.data.setNewBigWinReach(n);
                if (
                  (a.length &&
                    e.add(
                      o.CONCURRENT,
                      new l(l.SHOW_JP_WIN),
                      o.AFTER_PREVIOUS,
                      new l(l.SHOW_JP)
                    ),
                  i && i > 0)
                )
                  e.add(o.AFTER_PREVIOUS, new l(l.SHOW_TREASURE_VIEW, null));
                else if (r && !a.length) {
                  var c = { winnings: n, isRoundWin: !1 };
                  e.add(o.CONCURRENT, new l(l.SHOW_BIGWIN, c));
                }
                return (
                  this.data.isOpenEarlyFlag
                    ? e.add(
                        o.AFTER_PREVIOUS,
                        new l(l.SPIN_CLOSED_FLOW, null, { autoComplete: !0 })
                      )
                    : e.add(
                        o.AFTER_PREVIOUS,
                        new s(
                          s.SEND_CLOSE_REQUEST,
                          this.data.getData().spinId,
                          { autoComplete: !0 }
                        )
                      ),
                  e
                );
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(r);
                  },
                },
              ]),
              a
            );
          })(i).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateNewEarlySpinFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./StakeModel.ts",
    "./GameData.ts",
    "./FlowIDs.ts",
    "./SlotFrameworkEvent.ts",
    "./types.ts",
    "./Bundles.ts",
    "./DefinitionModel.ts",
    "./PlatformModel.ts",
    "./type2.ts",
    "./MathUtil.ts",
  ],
  function (t) {
    "use strict";
    var e, a, n, i, o, r, s, u, l, c, d, f, p, g, h;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose), (a = t.createClass);
        },
        function (t) {
          n = t.cclegacy;
        },
        function (t) {
          i = t.FlowTrigger;
        },
        function (t) {
          o = t.SingletonExtends;
        },
        function (t) {
          r = t.default;
        },
        function (t) {
          s = t.default;
        },
        function (t) {
          u = t.FlowIDs;
        },
        function (t) {
          l = t.SlotFrameworkEvent;
        },
        function (t) {
          c = t.EGameType;
        },
        function (t) {
          d = t.EBundles;
        },
        function (t) {
          f = t.default;
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          g = t.ESpinStatus;
        },
        function (t) {
          h = t.default;
        },
      ],
      execute: function () {
        n._RF.push(
          {},
          "83462N00pxPU445HuZWU4el",
          "CreateNewEarlySpinFlowCmd",
          void 0
        );
        t(
          "default",
          (function (t) {
            function n() {
              return t.apply(this, arguments) || this;
            }
            e(n, t);
            var o = n.prototype;
            return (
              (o.execute = function (t) {
                var e = this.createFlow(t);
                App.flowManager.registerFlow(e);
              }),
              (o.createFlow = function (t) {
                return this.createMgFlow(t);
              }),
              (o.createMgFlow = function (t) {
                var e = new App.flowManager.Flow(u.EARLY_SPIN_FLOW),
                  a = t.data.data,
                  n = (a.spinId, a.cheat),
                  o = {
                    ratioIndex: r.ratioIndex,
                    ratioValue: r.ratioValue,
                    stakeIndex: r.stakeIndex,
                    stakeValue: r.stakeValue,
                  };
                if (
                  0 === p.getData().player.balance.amount &&
                  this.data.currentGameType === c.MAIN_GAME
                )
                  return (this.data.isOpenEarlyFlag = !1), e;
                if (
                  !this.checkBalance() &&
                  this.data.currentGameType === c.MAIN_GAME
                ) {
                  this.data.isOpenEarlyFlag = !1;
                  var s = {
                      text: App.getLanguage(
                        "insufficientFund",
                        [],
                        d[d.wrapper]
                      ),
                      confirmCb: function () {
                        f();
                      },
                      bbrCb: function () {
                        f();
                      },
                    },
                    f = function () {
                      dispatch(l.SHOW_AUTO_SPIN, { data: !0 }),
                        dispatch(l.UPDATE_SPIN_STATUS, { data: g.IDLE });
                    };
                  return (
                    setTimeout(function () {
                      App.gameAlert.show(s);
                    }, 500),
                    dispatch(l.STOP_AUTO_SPIN),
                    e
                  );
                }
                var h = this.data.getData().spinId;
                return (
                  p.getData().isInstantClose &&
                    1 == p.getData().isInstantClose &&
                    (h = null),
                  e.add(
                    i.CONCURRENT,
                    new l(
                      l.SEND_EARLY_SPIN_REQUEST,
                      { spinId: "", stakeVO: o, cheat: n, forceClose: h },
                      { autoComplete: !0 }
                    )
                  ),
                  e
                );
              }),
              (o.checkBalance = function () {
                var t = {
                    ratioIndex: r.ratioIndex,
                    ratioValue: r.ratioValue,
                    stakeIndex: r.stakeIndex,
                    stakeValue: r.stakeValue,
                  },
                  e = t.stakeValue,
                  a = t.ratioValue,
                  n = f.getData().winlineDefs.length,
                  i = h.multiply(a, e, n);
                return p.getData().player.balance.amount - i >= 0;
              }),
              a(n, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(s);
                  },
                },
              ]),
              n
            );
          })(o).instance()
        );
        n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateNewQuickStopFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkEvent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, o, l, i, u, S, r, s, _;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          o = e.FlowTrigger;
        },
        function (e) {
          l = e.SingletonExtends;
        },
        function (e) {
          i = e.SlotFrameworkEvent;
        },
        function (e) {
          (u = e.default), (S = e.EBTM);
        },
        function (e) {
          r = e.default;
        },
        function (e) {
          s = e.GameEvent;
        },
        function (e) {
          _ = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "645683LrqRECJ5QV1iYUn9c",
          "CreateNewQuickStopFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var l = a.prototype;
            return (
              (l.execute = function () {
                if ((u.quickStopCount++, u.canQuickStop && !u.isTurbo)) {
                  u.quickStopCount++;
                  var e = this.createFlow();
                  App.flowManager.killFlow(_.STOP_SPIN_FLOW),
                    App.flowManager.registerFlow(e),
                    (u.canQuickStop = !1),
                    (u.canQuickStopEarlySpin = !1);
                }
              }),
              (l.createFlow = function () {
                var e = new App.flowManager.Flow(_.QUICK_STOP_FLOW),
                  t = this.data.getData().parser.newTimesSymbols;
                return (
                  e.add(o.CONCURRENT, new s(s.START_QUICK_STOP)),
                  t.length &&
                    e.add(
                      o.CONCURRENT,
                      new s(s.SPEED_CHARACTER_FIRE_UP, null, {
                        autoComplete: !0,
                      })
                    ),
                  e.add(o.AFTER_PREVIOUS, new s(s.SHOW_SYMBOLS_QUICK_IN_ANIM)),
                  this.ShowWinFlow(e),
                  e
                );
              }),
              (l.ShowWinFlow = function (e) {
                var t = this.data.getData().gameState,
                  n = t.winSymbols,
                  a = t.totalWinnings,
                  l = t.timesSymbols,
                  r = t.timesUpgrade,
                  _ = t.action,
                  w = t.roundWinnings,
                  c = this.data.preSpinData,
                  E = null == c ? void 0 : c.winSymbols.length,
                  d = "freeSpin" == _,
                  p = d ? w : a,
                  T = this.data.getData().parser.newTimesSymbols.length
                    ? 0.8
                    : 0.3,
                  O = E && !n.length && l.length,
                  C = d ? w : a,
                  m = this.data.setNewBigWinReach(C),
                  I = u.getData().winAmountTime;
                n.length &&
                  (e.add(
                    o.AFTER_PREVIOUS,
                    new s(s.SHOW_WIN_CASH, null, {
                      autoComplete: !0,
                      delay: T,
                    }),
                    new s(
                      s.UPDATE_WIN_AMOUNT,
                      { value: p },
                      { autoComplete: !0 }
                    ),
                    new i(
                      i.UPDATE_TOTAL_WINNINGS,
                      { value: a, tweenTime: I },
                      { autoComplete: !0 }
                    ),
                    new s(
                      s.PLAY_BTM,
                      { url: S.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new s(s.SHOW_SYMBOLS_WIN),
                    new s(s.SHOW_FULL_COMBO),
                    new s(s.REMOVE_SYMBOLS, null, { delay: 0.5 }),
                    new s(s.PLAY_CURRENT_VIEW_FALL_ANIM)
                  ),
                  r.length &&
                    e.add(
                      o.AFTER_PREVIOUS,
                      new s(s.SHOW_TIMES_SYMBOLS_UPGRADE, null, {
                        autoComplete: !0,
                      })
                    )),
                  O &&
                    (m
                      ? e.add(
                          o.AFTER_PREVIOUS,
                          new s(s.SHOW_TIMES_MOVING, null, { delay: 0.8 })
                        )
                      : e.add(
                          o.AFTER_PREVIOUS,
                          new s(s.SHOW_TIMES_MOVING, null, { delay: 0.8 }),
                          new s(
                            s.PLAY_BTM,
                            { url: S.COUNTING },
                            { autoComplete: !0 }
                          ),
                          new i(i.UPDATE_TOTAL_WINNINGS, {
                            value: a,
                            needComplete: !0,
                            tweenTime: I,
                          })
                        )),
                  e.add(
                    o.AFTER_PREVIOUS,
                    new s(s.CREATE_SPIN_COMPLETE_FLOW, null, {
                      autoComplete: !0,
                    })
                  );
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(r);
                  },
                },
              ]),
              a
            );
          })(l).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateNewResumeFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./type2.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, o, l, i, u, s, r, S, d, _, w;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          o = e.FlowTrigger;
        },
        function (e) {
          l = e.SingletonExtends;
        },
        function (e) {
          i = e.default;
        },
        function (e) {
          u = e.SlotFrameworkEvent;
        },
        function (e) {
          s = e.ESpinStatus;
        },
        function (e) {
          (r = e.default), (S = e.EBTM);
        },
        function (e) {
          d = e.default;
        },
        function (e) {
          _ = e.GameEvent;
        },
        function (e) {
          w = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "cb7a5aAGtVKmLOEGqORcyeo",
          "CreateNewResumeFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var l = a.prototype;
            return (
              (l.execute = function () {
                var e = this.createFlow();
                App.flowManager.registerFlow(e);
              }),
              (l.createFlow = function () {
                var e = new App.flowManager.Flow(w.RESUME_FLOW);
                return (
                  dispatch(u.UPDATE_USER_SPIN_ID, {
                    data: { spinId: this.data.getData().spinId },
                  }),
                  dispatch(u.UPDATE_SPIN_STATUS, { data: s.SPINING }),
                  dispatch(_.UPDATE_GAME_TYPE, {
                    data: this.data.currentGameType,
                  }),
                  this.ShowWinFlow(e),
                  e
                );
              }),
              (l.ShowWinFlow = function (e) {
                var t = this.data.getData().gameState,
                  n = t.winSymbols,
                  a = t.totalWinnings,
                  l = t.timesSymbols,
                  i = t.timesUpgrade,
                  s = t.action,
                  d = t.roundWinnings,
                  w = this.data.preSpinData,
                  E = null == w ? void 0 : w.winSymbols.length,
                  c = "freeSpin" == s,
                  p = c ? d : a,
                  T = this.data.getData().parser.newTimesSymbols.length
                    ? 0.8
                    : 0.3,
                  m = E && !n.length && l.length,
                  I = c ? d : a,
                  g = this.data.setNewBigWinReach(I),
                  A = r.getData().winAmountTime;
                n.length &&
                  (e.add(
                    o.AFTER_PREVIOUS,
                    new _(_.SHOW_WIN_CASH, null, {
                      autoComplete: !0,
                      delay: T,
                    }),
                    new _(
                      _.UPDATE_WIN_AMOUNT,
                      { value: p },
                      { autoComplete: !0 }
                    ),
                    new u(
                      u.UPDATE_TOTAL_WINNINGS,
                      { value: a, tweenTime: A },
                      { autoComplete: !0 }
                    ),
                    new _(
                      _.PLAY_BTM,
                      { url: S.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new _(_.SHOW_SYMBOLS_WIN),
                    new _(_.SHOW_FULL_COMBO),
                    new _(_.REMOVE_SYMBOLS, null, { delay: 0.5 }),
                    new _(_.PLAY_CURRENT_VIEW_FALL_ANIM)
                  ),
                  i.length &&
                    e.add(
                      o.AFTER_PREVIOUS,
                      new _(_.SHOW_TIMES_SYMBOLS_UPGRADE, null, {
                        autoComplete: !0,
                      })
                    )),
                  m &&
                    (g
                      ? e.add(
                          o.AFTER_PREVIOUS,
                          new _(_.SHOW_TIMES_MOVING, null, { delay: 0.8 })
                        )
                      : e.add(
                          o.AFTER_PREVIOUS,
                          new _(_.SHOW_TIMES_MOVING, null, { delay: 0.8 }),
                          new _(
                            _.PLAY_BTM,
                            { url: S.COUNTING },
                            { autoComplete: !0 }
                          ),
                          new u(u.UPDATE_TOTAL_WINNINGS, {
                            value: a,
                            needComplete: !0,
                            tweenTime: A,
                          })
                        )),
                  e.add(
                    o.AFTER_PREVIOUS,
                    new _(_.CREATE_SPIN_COMPLETE_FLOW, null, {
                      autoComplete: !0,
                    })
                  );
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(d);
                  },
                },
                {
                  key: "slotData",
                  get: function () {
                    return App.dataCenter.get(i);
                  },
                },
              ]),
              a
            );
          })(l).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateNewSpinCompleteFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./StakeModel.ts",
    "./SlotFrameworkEvent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameSymbolID.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var n, t, a, l, o, i, u, s, w, _, r, T, S;
    return {
      setters: [
        function (e) {
          (n = e.inheritsLoose), (t = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          l = e.FlowTrigger;
        },
        function (e) {
          o = e.SingletonExtends;
        },
        function (e) {
          i = e.default;
        },
        function (e) {
          u = e.SlotFrameworkEvent;
        },
        function (e) {
          (s = e.default), (w = e.EBTM);
        },
        function (e) {
          _ = e.default;
        },
        function (e) {
          r = e.EBackendSymbolID;
        },
        function (e) {
          T = e.GameEvent;
        },
        function (e) {
          S = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "45c04jeV5FOBKFKMd1FBEdB",
          "CreateNewSpinCompleteFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            n(a, e);
            var o = a.prototype;
            return (
              (o.execute = function () {
                this.createFlow();
              }),
              (o.createFlow = function () {
                var e = this.data.currSpinData,
                  n = e.currentView,
                  t = e.totalViews,
                  a = e.startFreeGame,
                  l = e.action,
                  o = n + 1 === t,
                  i = o && "freeSpin" == l;
                a
                  ? this.showFreeGameIntroFlow()
                  : o
                  ? i
                    ? this.freeGameFinishFlow()
                    : this.closeSpinFlow()
                  : this.nextSpinFlow();
              }),
              (o.showFreeGameIntroFlow = function () {
                var e = new App.flowManager.Flow(S.SHOW_FG_INTRO_FLOW),
                  n = this.data.currSpinData.totalWinnings,
                  t = this.data.setNewBigWinReach(n),
                  a = s.getData().winAmountTime;
                if (t) {
                  var o = { winnings: n, isRoundWin: !0 };
                  e.add(
                    l.CONCURRENT,
                    new T(T.SHOW_SCATTER_WIN, null, { delay: 0.3 }),
                    l.AFTER_PREVIOUS,
                    new T(T.SHOW_BIGWIN, o, { delay: 1 }),
                    new T(T.SHOW_FG_INTRO_ALERT, null, {
                      autoComplete: !0,
                      delay: 1,
                    })
                  );
                } else
                  e.add(
                    l.CONCURRENT,
                    new T(T.SHOW_SCATTER_WIN, null, { delay: 0.3 }),
                    l.AFTER_PREVIOUS,
                    new T(
                      T.UPDATE_WIN_AMOUNT,
                      { value: n },
                      { autoComplete: !0 }
                    ),
                    new T(
                      T.PLAY_BTM,
                      { url: w.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new u(u.UPDATE_TOTAL_WINNINGS, {
                      value: n,
                      needComplete: !0,
                      tweenTime: a,
                    }),
                    new T(T.SHOW_FG_INTRO_ALERT, null, { autoComplete: !0 })
                  );
                App.flowManager.registerFlow(e);
              }),
              (o.nextSpinFlow = function () {
                var e = new App.flowManager.Flow(S.NEXT_SPIN_FLOW),
                  n = this.data.getData().parser,
                  t = n.newTimesSymbols,
                  a = n.view1D,
                  o = this.data.currSpinData,
                  w = o.spinId,
                  _ = o.winSymbols,
                  d = o.roundWinnings,
                  N = o.action,
                  E = s.getData(),
                  p = E.hasTimesSymbolsDelay,
                  O = E.nextSpinDelay,
                  F = t.length ? p : O;
                if (_.length) {
                  i.ratioIndex, i.ratioValue, i.stakeIndex, i.stakeValue;
                  e.add(
                    l.AFTER_PREVIOUS,
                    new T(
                      T.CREATE_SPIN_FLOW,
                      { spinId: w, cheat: null, next: !0 },
                      { autoComplete: !0, delay: F }
                    )
                  );
                } else {
                  if ("freeSpin" == N) {
                    if (this.data.setNewBigWinReach(d)) {
                      var I = { winnings: d, isRoundWin: !0 };
                      e.add(
                        l.CONCURRENT,
                        new u(T.SHOW_BIGWIN, I, { delay: 0.5 })
                      );
                    }
                    a.filter(function (e) {
                      return e == r.SCATTER;
                    }).length >= 3 &&
                      e.add(
                        l.CONCURRENT,
                        new T(T.SHOW_SCATTER_WIN, null, { delay: 0.8 }),
                        l.AFTER_PREVIOUS,
                        new T(T.INCREASE_FG_REMAINING)
                      );
                  }
                  e.add(
                    l.AFTER_PREVIOUS,
                    new T(
                      T.CREATE_SPIN_FLOW,
                      { spinId: w, cheat: null, next: !0 },
                      { autoComplete: !0, delay: F }
                    )
                  );
                }
                App.flowManager.registerFlow(e);
              }),
              (o.freeGameFinishFlow = function () {
                var e = new App.flowManager.Flow(S.SHOW_FG_SUMMARY_FLOW),
                  n = this.data.currSpinData,
                  t = n.totalWinnings,
                  a = n.roundWinnings,
                  o = this.data.getData().spinId,
                  i = this.data.setNewBigWinReach(a),
                  _ = this.data.setNewBigWinReach(t),
                  r = s.getData().winAmountTime;
                if (i) {
                  var d = { winnings: a, isRoundWin: !0 };
                  e.add(
                    l.CONCURRENT,
                    new T(
                      T.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0, delay: 2.5 }
                    ),
                    new u(
                      u.UPDATE_TOTAL_WINNINGS,
                      { value: 0, tweenTime: r },
                      { autoComplete: !0 }
                    ),
                    new T(T.SHOW_BIGWIN, d)
                  );
                }
                if (_) {
                  var N = { winnings: t, isRoundWin: !1, isFgOut: !0 };
                  e.add(
                    l.AFTER_PREVIOUS,
                    new u(u.SEND_CLOSE_REQUEST, o, { autoComplete: !0 }),
                    new T(T.FG_STOP_COUNT_FOR_PLAY_LOG, null, {
                      autoComplete: !0,
                    }),
                    new T(T.SHOW_FG_SUMMARY_ALERT, null, { delay: 1 }),
                    new T(
                      T.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0, delay: 1.8 }
                    ),
                    new u(
                      u.UPDATE_TOTAL_WINNINGS,
                      { value: 0, tweenTime: r },
                      { autoComplete: !0 }
                    ),
                    new T(T.SHOW_BIGWIN, N),
                    new T(T.SPIN_CLOSED_FLOW, null, { autoComplete: !0 })
                  );
                } else
                  e.add(
                    l.AFTER_PREVIOUS,
                    new u(u.SEND_CLOSE_REQUEST, o, { autoComplete: !0 }),
                    new T(T.FG_STOP_COUNT_FOR_PLAY_LOG, null, {
                      autoComplete: !0,
                    }),
                    new T(T.SHOW_FG_SUMMARY_ALERT, null, { delay: 1 }),
                    new T(
                      T.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0 }
                    ),
                    new u(
                      u.UPDATE_TOTAL_WINNINGS,
                      { value: 0, tweenTime: r },
                      { autoComplete: !0 }
                    ),
                    new T(
                      T.UPDATE_WIN_AMOUNT,
                      { value: t },
                      { autoComplete: !0, delay: 1.8 }
                    ),
                    new T(
                      T.PLAY_BTM,
                      { url: w.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new u(u.UPDATE_TOTAL_WINNINGS, {
                      value: t,
                      needComplete: !0,
                      tweenTime: r,
                    }),
                    new T(T.SPIN_CLOSED_FLOW, null, { autoComplete: !0 })
                  );
                App.flowManager.registerFlow(e);
              }),
              (o.closeSpinFlow = function () {
                dispatch(T.CREATE_CLOSE_SPIN_FLOW);
              }),
              t(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(_);
                  },
                },
              ]),
              a
            );
          })(o).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateNewSpinFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./ObjectUtils.ts",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkData.ts",
    "./StakeModel.ts",
    "./SlotFrameworkEvent.ts",
    "./DefinitionModel.ts",
    "./PlatformModel.ts",
    "./SettingsModel.ts",
    "./type2.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./FlowIDs.ts",
    "./MathUtil.ts",
  ],
  function (t) {
    "use strict";
    var e, a, n, i, u, o, l, s, r, d, c, p, f, S, g, A, I, E, _, m, T;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose), (a = t.createClass);
        },
        function (t) {
          n = t.cclegacy;
        },
        function (t) {
          i = t.EBundles;
        },
        function (t) {
          u = t.ObjectUtils;
        },
        function (t) {
          o = t.FlowTrigger;
        },
        function (t) {
          l = t.SingletonExtends;
        },
        function (t) {
          s = t.default;
        },
        function (t) {
          r = t.default;
        },
        function (t) {
          d = t.default;
        },
        function (t) {
          c = t.SlotFrameworkEvent;
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          f = t.default;
        },
        function (t) {
          S = t.default;
        },
        function (t) {
          g = t.ESpinStatus;
        },
        function (t) {
          A = t.default;
        },
        function (t) {
          I = t.default;
        },
        function (t) {
          E = t.GameEvent;
        },
        function (t) {
          _ = t.EGameType;
        },
        function (t) {
          m = t.FlowIDs;
        },
        function (t) {
          T = t.default;
        },
      ],
      execute: function () {
        n._RF.push(
          {},
          "8d212HFB61JQY+gFegZ3VM3",
          "CreateNewSpinFlowCmd",
          void 0
        );
        t(
          "default",
          (function (t) {
            function n() {
              return t.apply(this, arguments) || this;
            }
            e(n, t);
            var l = n.prototype;
            return (
              (l.execute = function (t) {
                dispatch(E.SPIN_START),
                  (this.data.isSendOutEarlyFlag = !1),
                  (this.data.isSendClose = !1);
                var e = this.createSpinFlow(t);
                App.flowManager.registerFlow(e);
              }),
              (l.createSpinFlow = function (t) {
                var e = new App.flowManager.Flow(m.SPIN_FLOW);
                return App.uiManager.IsOnlyGameViewOpen("GameView")
                  ? (dispatch(c.UPDATE_SPIN_STATUS, { data: g.SPINING }),
                    t.data.next
                      ? this.nextSpinFlow(e, t)
                      : this.firstSpinFlow(e, t),
                    e)
                  : (Log.e("spin前提不能有其他UI在畫面上，所以不執行 SpinFlow"),
                    e);
              }),
              (l.firstSpinFlow = function (t, e) {
                var a = e.data,
                  n = a.spinId,
                  u = a.cheat,
                  l = A.getData().winAmountTime,
                  s = {
                    ratioIndex: d.ratioIndex,
                    ratioValue: d.ratioValue,
                    stakeIndex: d.stakeIndex,
                    stakeValue: d.stakeValue,
                  };
                if (
                  0 === f.getData().player.balance.amount &&
                  this.data.currentGameType === _.MAIN_GAME &&
                  !this.data.getData().isResuming
                ) {
                  var r = {
                      text: App.getLanguage(
                        "insufficientFundError",
                        [],
                        i[i.wrapper]
                      ),
                      confirmCb: function () {
                        p();
                      },
                      bbrCb: function () {
                        p();
                      },
                    },
                    p = function () {
                      dispatch(c.SHOW_AUTO_SPIN, { data: !0 }),
                        dispatch(c.UPDATE_SPIN_STATUS, { data: g.IDLE });
                    };
                  return (
                    (this.data.isOpenEarlyFlag = !1),
                    (this.data.isSendOutEarlyFlag = !1),
                    App.gameAlert.show(r),
                    void dispatch(c.STOP_AUTO_SPIN)
                  );
                }
                if (
                  !this.checkBalance() &&
                  this.data.currentGameType === _.MAIN_GAME &&
                  !this.data.getData().isResuming
                ) {
                  var S = {
                      text: App.getLanguage(
                        "insufficientFund",
                        [],
                        i[i.wrapper]
                      ),
                      confirmCb: function () {
                        I();
                      },
                      bbrCb: function () {
                        I();
                      },
                    },
                    I = function () {
                      dispatch(c.SHOW_AUTO_SPIN, { data: !0 }),
                        dispatch(c.UPDATE_SPIN_STATUS, { data: g.IDLE });
                    };
                  return (
                    (this.data.isSendOutEarlyFlag = !1),
                    (this.data.isOpenEarlyFlag = !1),
                    App.gameAlert.show(S),
                    void dispatch(c.STOP_AUTO_SPIN)
                  );
                }
                this.data.currentGameType == _.MAIN_GAME &&
                  (Log.e("spinId::::::::", n),
                  null != n && "" != n
                    ? (Log.e("buy feature:::::::::::"),
                      (f.amount = this.getAfterBuyFeatureBalance()))
                    : (f.amount = this.getAfterBettingBalance())),
                  n ||
                    t.add(
                      o.CONCURRENT,
                      new c(
                        c.UPDATE_TOTAL_WINNINGS,
                        { value: 0, tweenTime: l },
                        { autoComplete: !0 }
                      )
                    ),
                  this.calculateAutoSpin(),
                  t.add(
                    o.CONCURRENT,
                    new E(
                      E.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0 }
                    ),
                    new E(c.PLAY_SPIN_BTN_RELEASED_ANIM, null, {
                      autoComplete: !0,
                    })
                  ),
                  t.add(
                    o.CONCURRENT,
                    new E(
                      c.UPDATE_USER_BALANCE,
                      { balance: f.amount },
                      { autoComplete: !0 }
                    )
                  ),
                  this.data.isOpenEarlyFlag
                    ? t.add(
                        o.AFTER_PREVIOUS,
                        new E(E.SHOW_SYMBOLS_OUT_ANIM),
                        o.AFTER_PREVIOUS,
                        new E(E.EARLY_DATA_PARSER_TO_SPIN_DATA, null, {
                          autoComplete: !0,
                        })
                      )
                    : t.add(
                        o.AFTER_PREVIOUS,
                        new E(E.SHOW_SYMBOLS_OUT_ANIM),
                        o.CONCURRENT,
                        new E(
                          c.SEND_SPIN_REQUEST,
                          {
                            spinId: n,
                            stakeVO: s,
                            cheat: u,
                            updateStake: this.needUpdateStake(),
                          },
                          { autoComplete: !0 }
                        )
                      );
              }),
              (l.nextSpinFlow = function (t, e) {
                this.data.setNextSpinData(),
                  "freeSpin" == this.data.currSpinData.action &&
                    this.data.preSpinData.winSymbols &&
                    0 == this.data.preSpinData.winSymbols.length &&
                    t.add(
                      o.CONCURRENT,
                      new E(
                        E.UPDATE_WIN_AMOUNT,
                        { value: 0 },
                        { autoComplete: !0 }
                      ),
                      new E(c.PLAY_SPIN_BTN_RELEASED_ANIM, null, {
                        autoComplete: !0,
                      })
                    ),
                  t.add(
                    o.AFTER_PREVIOUS,
                    new E(E.CREATE_STOP_SPIN_FLOW, null, { autoComplete: !0 })
                  );
              }),
              (l.checkBalance = function () {
                var t = {
                    ratioIndex: d.ratioIndex,
                    ratioValue: d.ratioValue,
                    stakeIndex: d.stakeIndex,
                    stakeValue: d.stakeValue,
                  },
                  e = t.stakeValue,
                  a = t.ratioValue,
                  n = p.getData().winlineDefs.length,
                  i = T.multiply(a, e, n);
                return f.getData().player.balance.amount - i >= 0;
              }),
              (l.needUpdateStake = function () {
                var t = { stakeIndex: S.stakeIndex, ratioIndex: S.ratioIndex },
                  e = { stakeIndex: d.stakeIndex, ratioIndex: d.ratioIndex },
                  a = u.diffObjects(t, e);
                return Object.keys(a).length > 0;
              }),
              (l.calculateAutoSpin = function () {
                if (s.active && s.spinsRemaining > 0) {
                  if (this.data.currentGameType === _.FREE_GAME) return;
                  s.spinsRemaining--;
                }
              }),
              (l.getAfterBettingBalance = function () {
                var t = {
                    ratioIndex: d.ratioIndex,
                    ratioValue: d.ratioValue,
                    stakeIndex: d.stakeIndex,
                    stakeValue: d.stakeValue,
                  },
                  e = t.stakeValue,
                  a = t.ratioValue,
                  n = p.getData().winlineDefs.length,
                  i = T.multiply(a, e, n);
                return (
                  Log.e("stake::::::::", i),
                  Log.e(
                    "balance::::::::::::",
                    f.getData().player.balance.amount - i
                  ),
                  f.getData().player.balance.amount - i
                );
              }),
              (l.getAfterBuyFeatureBalance = function () {
                var t = {
                    ratioIndex: d.ratioIndex,
                    ratioValue: d.ratioValue,
                    stakeIndex: d.stakeIndex,
                    stakeValue: d.stakeValue,
                  },
                  e = t.stakeValue,
                  a = t.ratioValue,
                  n = p.getData().winlineDefs.length,
                  i = this.data.getData().definition.buyFeature,
                  u = T.multiply(a, e, n) * i[0].featureRate;
                return (
                  Log.e("featureStake::::::::", u),
                  Log.e(
                    "balance::::::::::::",
                    f.getData().player.balance.amount - u
                  ),
                  f.getData().player.balance.amount - u
                );
              }),
              a(n, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(I);
                  },
                },
                {
                  key: "slotData",
                  get: function () {
                    return App.dataCenter.get(r);
                  },
                },
              ]),
              n
            );
          })(l).instance()
        );
        n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateNewStopSpinFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkEvent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, l, o, i, s, r, S, u, w;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          l = e.FlowTrigger;
        },
        function (e) {
          o = e.SingletonExtends;
        },
        function (e) {
          i = e.SlotFrameworkEvent;
        },
        function (e) {
          (s = e.default), (r = e.EBTM);
        },
        function (e) {
          S = e.default;
        },
        function (e) {
          u = e.GameEvent;
        },
        function (e) {
          w = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "afaa4EnxJRMi6h6vvMEZL0I",
          "CreateNewStopSpinFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var o = a.prototype;
            return (
              (o.execute = function () {
                var e = this.createFlow();
                App.flowManager.registerFlow(e);
              }),
              (o.createFlow = function () {
                var e = new App.flowManager.Flow(w.STOP_SPIN_FLOW),
                  t = this.data.preSpinData,
                  n = this.data.getData().parser.newTimesSymbols,
                  a = this.data.currSpinData,
                  o = a.currentView,
                  i = a.action,
                  r = a.currentTimes,
                  S = t.winSymbols.length;
                return (
                  this.data.isOpenEarlyFlag && this.createEarlySpinFlow(),
                  "freeSpin" == i &&
                    (dispatch(u.UPDATE_FG_REMAINING),
                    dispatch(u.UPDATE_FG_TOTAL_TIMES, { data: r })),
                  n.length && this.showCharacterFireFlow(e),
                  0 !== o && S
                    ? this.newSymBolsInFlow(e)
                    : (o > 0
                        ? ((s.canQuickStop = !0),
                          e.add(
                            l.AFTER_PREVIOUS,
                            new u(u.SHOW_SYMBOLS_OUT_ANIM)
                          ))
                        : (s.canQuickStop = !0),
                      this.allSymbolsInFlow(e)),
                  this.ShowWinFlow(e),
                  e
                );
              }),
              (o.showCharacterFireFlow = function (e) {
                e.add(
                  l.CONCURRENT,
                  new u(u.SHOW_CHARACTER_FIRE, null, { autoComplete: !0 })
                );
              }),
              (o.allSymbolsInFlow = function (e) {
                e.add(l.AFTER_PREVIOUS, new u(u.SHOW_SYMBOLS_IN_ANIM));
              }),
              (o.newSymBolsInFlow = function (e) {
                var t = this.data.getData().parser.newTimesSymbols.length
                  ? 0.3
                  : 0;
                e.add(
                  l.CONCURRENT,
                  new u(u.SHOW_NEW_SYMBOLS_IN_ANIM, null, { delay: t })
                );
              }),
              (o.ShowWinFlow = function (e) {
                var t = this.data.getData().gameState,
                  n = t.winSymbols,
                  a = t.totalWinnings,
                  o = t.timesSymbols,
                  S = t.timesUpgrade,
                  w = t.action,
                  _ = t.roundWinnings,
                  d = this.data.preSpinData,
                  E = null == d ? void 0 : d.winSymbols.length,
                  c = "freeSpin" == w,
                  p = c ? _ : a,
                  T = this.data.getData().parser.newTimesSymbols.length
                    ? 0.8
                    : 0.3,
                  I = E && !n.length && o.length,
                  O = c ? _ : a,
                  h = this.data.setNewBigWinReach(O),
                  F = s.getData().winAmountTime;
                n.length &&
                  (e.add(
                    l.AFTER_PREVIOUS,
                    new u(u.SHOW_WIN_CASH, null, {
                      autoComplete: !0,
                      delay: T,
                    }),
                    new u(
                      u.UPDATE_WIN_AMOUNT,
                      { value: p },
                      { autoComplete: !0 }
                    ),
                    new i(
                      i.UPDATE_TOTAL_WINNINGS,
                      { value: a, tweenTime: F },
                      { autoComplete: !0 }
                    ),
                    new u(
                      u.PLAY_BTM,
                      { url: r.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new u(u.SHOW_SYMBOLS_WIN),
                    new u(u.SHOW_FULL_COMBO),
                    new u(u.REMOVE_SYMBOLS, null, { delay: 0.5 }),
                    new u(u.PLAY_CURRENT_VIEW_FALL_ANIM)
                  ),
                  S.length &&
                    e.add(
                      l.AFTER_PREVIOUS,
                      new u(u.SHOW_TIMES_SYMBOLS_UPGRADE, null, {
                        autoComplete: !0,
                      })
                    )),
                  I &&
                    (h
                      ? e.add(
                          l.AFTER_PREVIOUS,
                          new u(u.SHOW_TIMES_MOVING, null, { delay: 0.8 })
                        )
                      : e.add(
                          l.AFTER_PREVIOUS,
                          new u(u.SHOW_TIMES_MOVING, null, { delay: 0.8 }),
                          new u(
                            u.PLAY_BTM,
                            { url: r.COUNTING },
                            { autoComplete: !0 }
                          ),
                          new i(i.UPDATE_TOTAL_WINNINGS, {
                            value: a,
                            needComplete: !0,
                            tweenTime: F,
                          })
                        )),
                  e.add(
                    l.AFTER_PREVIOUS,
                    new u(u.CREATE_SPIN_COMPLETE_FLOW, null, {
                      autoComplete: !0,
                    })
                  );
              }),
              (o.createEarlySpinFlow = function () {
                var e = {
                  data: {
                    spinId: this.data.getData().gameState.spinId,
                    cheat: null,
                  },
                };
                dispatch(u.CREATE_EARLY_SPIN_FLOW, { data: e });
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(S);
                  },
                },
              ]),
              a
            );
          })(o).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateReplayCloseSpinFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkEvent.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var n, t, a, l, o, i, r, s, u;
    return {
      setters: [
        function (e) {
          (n = e.inheritsLoose), (t = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          l = e.FlowTrigger;
        },
        function (e) {
          o = e.SingletonExtends;
        },
        function (e) {
          i = e.SlotFrameworkEvent;
        },
        function (e) {
          r = e.default;
        },
        function (e) {
          s = e.GameEvent;
        },
        function (e) {
          u = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "0e795oVhelFyr31kxAU1xmr",
          "CreateReplayCloseSpinFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            n(a, e);
            var o = a.prototype;
            return (
              (o.execute = function () {
                var e = this.createFlow();
                App.flowManager.registerFlow(e);
              }),
              (o.createFlow = function () {
                var e = new App.flowManager.Flow(u.REPLAY_CLOSE_SPIN_FLOW),
                  n = this.data.getData().gameState,
                  t = n.totalWinnings,
                  a = n.isJp,
                  o = n.noWinReward,
                  r = this.data.setBigWinReach(t);
                if (
                  (a.length &&
                    e.add(
                      l.CONCURRENT,
                      new s(s.SHOW_JP_WIN),
                      l.AFTER_PREVIOUS,
                      new s(s.SHOW_JP),
                      l.AFTER_PREVIOUS,
                      new i(i.SHOW_REPLAY_END, null, { delay: 0.3 })
                    ),
                  r && !a.length)
                ) {
                  var E = { winnings: t, isRoundWin: !1 };
                  null != o && o > 0
                    ? e.add(
                        l.AFTER_PREVIOUS,
                        new s(s.SHOW_TREASURE_VIEW, null),
                        new i(i.SHOW_REPLAY_END, null, { delay: 0.5 })
                      )
                    : e.add(
                        l.AFTER_PREVIOUS,
                        new s(s.SHOW_BIGWIN, E),
                        l.AFTER_PREVIOUS,
                        new i(i.SHOW_REPLAY_END, null, { delay: 0.3 })
                      );
                }
                return (
                  o &&
                    o > 0 &&
                    e.add(l.AFTER_PREVIOUS, new s(s.SHOW_TREASURE_VIEW, null)),
                  r ||
                    a.length ||
                    e.add(
                      l.AFTER_PREVIOUS,
                      new i(i.SHOW_REPLAY_END, null, { delay: 0.5 })
                    ),
                  e
                );
              }),
              t(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(r);
                  },
                },
              ]),
              a
            );
          })(o).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateReplayFlow.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./type2.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, l, o, i, u, r, s, S, _, E, d;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          l = e.FlowTrigger;
        },
        function (e) {
          o = e.SingletonExtends;
        },
        function (e) {
          i = e.default;
        },
        function (e) {
          u = e.SlotFrameworkEvent;
        },
        function (e) {
          r = e.ESpinStatus;
        },
        function (e) {
          (s = e.default), (S = e.EBTM);
        },
        function (e) {
          _ = e.default;
        },
        function (e) {
          E = e.GameEvent;
        },
        function (e) {
          d = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push({}, "e979060GTZKappgKyzZfPNV", "CreateReplayFlow", void 0);
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var o = a.prototype;
            return (
              (o.execute = function () {
                var e = this.createFlow();
                App.flowManager.registerFlow(e);
              }),
              (o.createFlow = function () {
                var e = new App.flowManager.Flow(d.REPLAY_RESUME_FLOW);
                return (
                  dispatch(u.UPDATE_SPIN_STATUS, { data: r.SPINING }),
                  dispatch(E.UPDATE_GAME_TYPE, {
                    data: this.data.currentGameType,
                  }),
                  this.ShowWinFlow(e),
                  e
                );
              }),
              (o.ShowWinFlow = function (e) {
                var t,
                  n = this.data.getData().gameState,
                  a = n.winSymbols,
                  o = n.totalWinnings,
                  i = n.timesSymbols,
                  r = n.timesUpgrade,
                  _ = n.action,
                  d = n.roundWinnings,
                  w =
                    null == (t = this.data.preData.gameState)
                      ? void 0
                      : t.winSymbols.length,
                  p = "freeSpin" == _,
                  c = p ? d : o,
                  T = this.data.getData().parser.newTimesSymbols.length
                    ? 0.8
                    : 0.3,
                  g = w && !a.length && i.length,
                  m = p ? d : o,
                  A = this.data.setBigWinReach(m),
                  f = s.getData().winAmountTime;
                e.add(
                  l.CONCURRENT,
                  new E("REPLAY_DELAY", null, { delay: 0.5, autoComplete: !0 })
                ),
                  a.length &&
                    (e.add(
                      l.AFTER_PREVIOUS,
                      new E(E.SHOW_WIN_CASH, null, {
                        autoComplete: !0,
                        delay: T,
                      }),
                      new E(
                        E.PLAY_BTM,
                        { url: S.COUNTING },
                        { autoComplete: !0 }
                      ),
                      new E(
                        E.UPDATE_WIN_AMOUNT,
                        { value: c },
                        { autoComplete: !0 }
                      ),
                      new u(
                        u.UPDATE_TOTAL_WINNINGS,
                        { value: o, tweenTime: f },
                        { autoComplete: !0 }
                      ),
                      new E(E.SHOW_SYMBOLS_WIN),
                      new E(E.SHOW_FULL_COMBO),
                      new E(E.REMOVE_SYMBOLS, null, { delay: 0.5 }),
                      new E(E.PLAY_CURRENT_VIEW_FALL_ANIM)
                    ),
                    r.length &&
                      e.add(
                        l.AFTER_PREVIOUS,
                        new E(E.SHOW_TIMES_SYMBOLS_UPGRADE, null, {
                          autoComplete: !0,
                        })
                      )),
                  g &&
                    (A
                      ? e.add(
                          l.AFTER_PREVIOUS,
                          new E(E.SHOW_TIMES_MOVING, null, { delay: 0.8 })
                        )
                      : e.add(
                          l.AFTER_PREVIOUS,
                          new E(E.SHOW_TIMES_MOVING, null, { delay: 0.8 }),
                          new E(
                            E.PLAY_BTM,
                            { url: S.COUNTING },
                            { autoComplete: !0 }
                          ),
                          new u(u.UPDATE_TOTAL_WINNINGS, {
                            value: o,
                            needComplete: !0,
                            tweenTime: f,
                          })
                        )),
                  e.add(
                    l.CONCURRENT,
                    new E(E.CREATE_REPLAY_SPIN_COMPLETE_FLOW, null, {
                      autoComplete: !0,
                    })
                  );
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(_);
                  },
                },
                {
                  key: "slotData",
                  get: function () {
                    return App.dataCenter.get(i);
                  },
                },
              ]),
              a
            );
          })(o).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateReplayQuickStopFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkEvent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, o, l, i, u, S, _, r, s;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          o = e.FlowTrigger;
        },
        function (e) {
          l = e.SingletonExtends;
        },
        function (e) {
          i = e.SlotFrameworkEvent;
        },
        function (e) {
          (u = e.default), (S = e.EBTM);
        },
        function (e) {
          _ = e.default;
        },
        function (e) {
          r = e.GameEvent;
        },
        function (e) {
          s = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "5e18annFcNBIJJSM06/5c15",
          "CreateReplayQuickStopFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var l = a.prototype;
            return (
              (l.execute = function () {
                if ((u.quickStopCount++, u.canQuickStop && !u.isTurbo)) {
                  u.quickStopCount++;
                  var e = this.createFlow();
                  App.flowManager.killFlow(s.REPLAY_STOP_SPIN_FLOW),
                    App.flowManager.registerFlow(e),
                    (u.canQuickStop = !1),
                    (u.canQuickStopEarlySpin = !1);
                }
              }),
              (l.createFlow = function () {
                var e = new App.flowManager.Flow(s.REPLAY_QUICK_STOP_FLOW),
                  t = this.data.getData().parser.newTimesSymbols;
                return (
                  e.add(o.CONCURRENT, new r(r.START_QUICK_STOP)),
                  t.length > 0 &&
                    e.add(
                      o.CONCURRENT,
                      new r(r.SPEED_CHARACTER_FIRE_UP, null, {
                        autoComplete: !0,
                      })
                    ),
                  e.add(o.AFTER_PREVIOUS, new r(r.SHOW_SYMBOLS_QUICK_IN_ANIM)),
                  this.ShowWinFlow(e),
                  e
                );
              }),
              (l.ShowWinFlow = function (e) {
                var t,
                  n = this.data.getData().gameState,
                  a = n.winSymbols,
                  l = n.totalWinnings,
                  _ = n.timesSymbols,
                  s = n.timesUpgrade,
                  w = n.action,
                  c = n.roundWinnings,
                  E =
                    null == (t = this.data.preData.gameState)
                      ? void 0
                      : t.winSymbols.length,
                  d = "freeSpin" == w,
                  p = d ? c : l,
                  T = this.data.getData().parser.newTimesSymbols.length
                    ? 0.8
                    : 0.3,
                  O = E && !a.length && _.length,
                  C = d ? c : l,
                  m = this.data.setBigWinReach(C),
                  I = u.getData().winAmountTime;
                a.length &&
                  (e.add(
                    o.AFTER_PREVIOUS,
                    new r(r.SHOW_WIN_CASH, null, {
                      autoComplete: !0,
                      delay: T,
                    }),
                    new r(
                      r.UPDATE_WIN_AMOUNT,
                      { value: p },
                      { autoComplete: !0 }
                    ),
                    new i(
                      i.UPDATE_TOTAL_WINNINGS,
                      { value: l, tweenTime: I },
                      { autoComplete: !0 }
                    ),
                    new r(
                      r.PLAY_BTM,
                      { url: S.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new r(r.SHOW_SYMBOLS_WIN),
                    new r(r.SHOW_FULL_COMBO),
                    new r(r.REMOVE_SYMBOLS, null, { delay: 0.5 }),
                    new r(r.PLAY_CURRENT_VIEW_FALL_ANIM)
                  ),
                  s.length &&
                    e.add(
                      o.AFTER_PREVIOUS,
                      new r(r.SHOW_TIMES_SYMBOLS_UPGRADE, null, {
                        autoComplete: !0,
                      })
                    )),
                  O &&
                    (m
                      ? e.add(
                          o.AFTER_PREVIOUS,
                          new r(r.SHOW_TIMES_MOVING, null, { delay: 0.8 })
                        )
                      : e.add(
                          o.AFTER_PREVIOUS,
                          new r(r.SHOW_TIMES_MOVING, null, { delay: 0.8 }),
                          new r(
                            r.PLAY_BTM,
                            { url: S.COUNTING },
                            { autoComplete: !0 }
                          ),
                          new i(i.UPDATE_TOTAL_WINNINGS, {
                            value: l,
                            needComplete: !0,
                            tweenTime: I,
                          })
                        )),
                  e.add(
                    o.AFTER_PREVIOUS,
                    new r(r.CREATE_REPLAY_SPIN_COMPLETE_FLOW, null, {
                      autoComplete: !0,
                    })
                  );
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(_);
                  },
                },
              ]),
              a
            );
          })(l).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateReplaySpinCompleteFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./SlotFrameworkEvent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameSymbolID.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, l, i, o, u, s, w, _, r, T;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          l = e.FlowTrigger;
        },
        function (e) {
          i = e.SingletonExtends;
        },
        function (e) {
          o = e.SlotFrameworkEvent;
        },
        function (e) {
          (u = e.default), (s = e.EBTM);
        },
        function (e) {
          w = e.default;
        },
        function (e) {
          _ = e.EBackendSymbolID;
        },
        function (e) {
          r = e.GameEvent;
        },
        function (e) {
          T = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "e02dbGSjjpLrIJ1Z8i8uqWd",
          "CreateReplaySpinCompleteFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var i = a.prototype;
            return (
              (i.execute = function () {
                this.createFlow();
              }),
              (i.createFlow = function () {
                var e = this.data.getData().gameState,
                  t = e.currentView,
                  n = e.totalViews,
                  a = e.startFreeGame,
                  l = e.action,
                  i = t + 1 === n,
                  o = i && "freeSpin" == l;
                a
                  ? this.showFreeGameIntroFlow()
                  : i
                  ? o
                    ? this.freeGameFinishFlow()
                    : this.closeSpinFlow()
                  : this.nextSpinFlow();
              }),
              (i.showFreeGameIntroFlow = function () {
                var e = new App.flowManager.Flow(T.REPLAY_SHOW_FG_INTRO_FLOW),
                  t = this.data.getData().gameState.totalWinnings,
                  n = this.data.setBigWinReach(t),
                  a = u.getData().winAmountTime;
                if (n) {
                  var i = { winnings: t, isRoundWin: !0 };
                  e.add(
                    l.CONCURRENT,
                    new r(r.SHOW_SCATTER_WIN, null, { delay: 0.3 }),
                    l.AFTER_PREVIOUS,
                    new r(r.SHOW_BIGWIN, i, { delay: 1 }),
                    new r(r.SHOW_FG_INTRO_ALERT, null, {
                      autoComplete: !0,
                      delay: 1,
                    })
                  );
                } else
                  e.add(
                    l.CONCURRENT,
                    new r(r.SHOW_SCATTER_WIN, null, { delay: 0.3 }),
                    l.AFTER_PREVIOUS,
                    new r(
                      r.PLAY_BTM,
                      { url: s.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new r(
                      r.UPDATE_WIN_AMOUNT,
                      { value: t },
                      { autoComplete: !0 }
                    ),
                    new o(
                      o.UPDATE_TOTAL_WINNINGS,
                      { value: t, needComplete: !0, tweenTime: a },
                      { autoComplete: !0 }
                    ),
                    new r(r.SHOW_FG_INTRO_ALERT, null, { autoComplete: !0 })
                  );
                App.flowManager.registerFlow(e);
              }),
              (i.nextSpinFlow = function () {
                var e = new App.flowManager.Flow(T.REPLAY_NEXT_SPIN_FLOW),
                  t = this.data.getData().parser,
                  n = t.newTimesSymbols,
                  a = t.view1D,
                  i = this.data.getData().gameState,
                  s = i.winSymbols,
                  w = i.roundWinnings,
                  d = i.action,
                  E = i.currentView,
                  N = u.getData(),
                  R = N.hasTimesSymbolsDelay,
                  S = N.nextSpinDelay,
                  A = n.length ? R : S;
                if (s.length) e.add(l.CONCURRENT, new o(o.REPLAY_NEXT_SPIN));
                else if ("freeSpin" == d) {
                  if (this.data.setBigWinReach(w)) {
                    var p = { winnings: w, isRoundWin: !0 };
                    e.add(
                      l.CONCURRENT,
                      new o(r.SHOW_BIGWIN, p, { delay: 0.5 })
                    );
                  }
                  a.filter(function (e) {
                    return e == _.SCATTER;
                  }).length >= 3 &&
                    e.add(
                      l.CONCURRENT,
                      new r(r.SHOW_SCATTER_WIN, null, { delay: 0.8 }),
                      l.AFTER_PREVIOUS,
                      new r(r.INCREASE_FG_REMAINING)
                    ),
                    e.add(
                      l.AFTER_PREVIOUS,
                      new r(r.CREATE_REPLAY_SPIN_FLOW, null, {
                        autoComplete: !0,
                        delay: A,
                      })
                    );
                }
                s.length ||
                  0 !== E ||
                  e.add(l.CONCURRENT, new o(o.REPLAY_NEXT_SPIN)),
                  App.flowManager.registerFlow(e);
              }),
              (i.freeGameFinishFlow = function () {
                var e = new App.flowManager.Flow(T.REPLAY_SHOW_FG_SUMMARY_FLOW),
                  t = this.data.getData().gameState,
                  n = t.totalWinnings,
                  a = t.roundWinnings,
                  i = this.data.setBigWinReach(a),
                  w = this.data.setBigWinReach(n),
                  _ = u.getData().winAmountTime;
                if (i) {
                  var d = { winnings: a, isRoundWin: !0 };
                  e.add(
                    l.CONCURRENT,
                    new r(
                      r.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0, delay: 2.5 }
                    ),
                    new o(
                      o.UPDATE_TOTAL_WINNINGS,
                      { value: 0, tweenTime: _ },
                      { autoComplete: !0 }
                    ),
                    new r(r.SHOW_BIGWIN, d)
                  );
                }
                if (w) {
                  var E = { winnings: n, isRoundWin: !1, isFgOut: !0 };
                  e.add(
                    l.AFTER_PREVIOUS,
                    new r(r.SHOW_FG_SUMMARY_ALERT, null, { delay: 1 }),
                    new r(
                      r.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0, delay: 1.8 }
                    ),
                    new o(
                      o.UPDATE_TOTAL_WINNINGS,
                      { value: 0, tweenTime: _ },
                      { autoComplete: !0 }
                    ),
                    new r(r.SHOW_BIGWIN, E),
                    new o(o.SHOW_REPLAY_END, null, { delay: 0.3 })
                  );
                } else
                  e.add(
                    l.AFTER_PREVIOUS,
                    new r(r.SHOW_FG_SUMMARY_ALERT, null, { delay: 1 }),
                    new r(
                      r.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0 }
                    ),
                    new o(
                      o.UPDATE_TOTAL_WINNINGS,
                      { value: 0, tweenTime: _ },
                      { autoComplete: !0 }
                    ),
                    new r(
                      r.UPDATE_WIN_AMOUNT,
                      { value: n },
                      { autoComplete: !0, delay: 1.8 }
                    ),
                    new r(
                      r.PLAY_BTM,
                      { url: s.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new o(o.UPDATE_TOTAL_WINNINGS, {
                      value: n,
                      needComplete: !0,
                      tweenTime: _,
                    }),
                    new o(o.SHOW_REPLAY_END, null, { delay: 0.3 })
                  );
                App.flowManager.registerFlow(e);
              }),
              (i.closeSpinFlow = function () {
                dispatch(r.CREATE_REPLAY_CLOSE_SPIN_FLOW);
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(w);
                  },
                },
              ]),
              a
            );
          })(i).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateReplaySpinFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./FlowIDs.ts",
  ],
  function (t) {
    "use strict";
    var e, n, a, o, i, r, u, l, s, c, p, f;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose), (n = t.createClass);
        },
        function (t) {
          a = t.cclegacy;
        },
        function (t) {
          o = t.FlowTrigger;
        },
        function (t) {
          i = t.SingletonExtends;
        },
        function (t) {
          r = t.default;
        },
        function (t) {
          u = t.default;
        },
        function (t) {
          l = t.SlotFrameworkEvent;
        },
        function (t) {
          s = t.default;
        },
        function (t) {
          c = t.GameEvent;
        },
        function (t) {
          p = t.EGameType;
        },
        function (t) {
          f = t.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "f7631a+AN9Kobu1HQl4bPtS",
          "CreateReplaySpinFlowCmd",
          void 0
        );
        t(
          "default",
          (function (t) {
            function a() {
              return t.apply(this, arguments) || this;
            }
            e(a, t);
            var i = a.prototype;
            return (
              (i.execute = function (t) {
                var e = this.createSpinFlow(t);
                App.flowManager.registerFlow(e);
              }),
              (i.createSpinFlow = function (t) {
                var e = new App.flowManager.Flow(f.REPLAY_SPIN_FLOW);
                return this.firstSpinFlow(e, t), e;
              }),
              (i.firstSpinFlow = function (t, e) {
                this.calculateAutoSpin(),
                  t.add(
                    o.CONCURRENT,
                    new c(
                      c.UPDATE_WIN_AMOUNT,
                      { value: 0 },
                      { autoComplete: !0 }
                    )
                  ),
                  t.add(o.CONCURRENT, new l(l.REPLAY_NEXT_SPIN));
              }),
              (i.calculateAutoSpin = function () {
                if (r.active && r.spinsRemaining > 0) {
                  if (this.data.currentGameType === p.FREE_GAME) return;
                  r.spinsRemaining--;
                }
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(s);
                  },
                },
                {
                  key: "slotData",
                  get: function () {
                    return App.dataCenter.get(u);
                  },
                },
              ]),
              a
            );
          })(i).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CreateReplayStopSpinFlowCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkEvent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./FlowIDs.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, l, o, i, s, r, u, S, _, d;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          l = e.FlowTrigger;
        },
        function (e) {
          o = e.SingletonExtends;
        },
        function (e) {
          i = e.default;
        },
        function (e) {
          s = e.SlotFrameworkEvent;
        },
        function (e) {
          (r = e.default), (u = e.EBTM);
        },
        function (e) {
          S = e.default;
        },
        function (e) {
          _ = e.GameEvent;
        },
        function (e) {
          d = e.FlowIDs;
        },
      ],
      execute: function () {
        a._RF.push(
          {},
          "7eeefpAoA1J4bTTlBHH8evo",
          "CreateReplayStopSpinFlowCmd",
          void 0
        );
        e(
          "default",
          (function (e) {
            function a() {
              return e.apply(this, arguments) || this;
            }
            t(a, e);
            var o = a.prototype;
            return (
              (o.execute = function () {
                var e = this.createFlow();
                App.flowManager.registerFlow(e);
              }),
              (o.createFlow = function () {
                var e,
                  t = new App.flowManager.Flow(d.REPLAY_STOP_SPIN_FLOW),
                  n = this.data.preData,
                  a = this.data.getData().parser.newTimesSymbols,
                  l = this.data.getData().gameState,
                  o = l.currentView,
                  i = l.action,
                  s = l.currentTimes,
                  u = null == (e = n.gameState) ? void 0 : e.winSymbols.length;
                return (
                  "freeSpin" == i &&
                    (dispatch(_.UPDATE_FG_REMAINING),
                    dispatch(_.UPDATE_FG_TOTAL_TIMES, { data: s })),
                  a.length && this.showCharacterFireFlow(t),
                  0 !== o && u
                    ? this.newSymBolsInFlow(t)
                    : ((r.canQuickStop = !0), this.allSymbolsInFlow(t)),
                  this.ShowWinFlow(t),
                  t
                );
              }),
              (o.showCharacterFireFlow = function (e) {
                e.add(
                  l.CONCURRENT,
                  new _(_.SHOW_CHARACTER_FIRE, null, { autoComplete: !0 })
                );
              }),
              (o.allSymbolsInFlow = function (e) {
                e.add(
                  l.CONCURRENT,
                  new _(_.SHOW_SYMBOLS_OUT_ANIM),
                  l.AFTER_PREVIOUS,
                  new _(_.SHOW_SYMBOLS_IN_ANIM)
                );
              }),
              (o.newSymBolsInFlow = function (e) {
                var t = this.data.getData().parser.newTimesSymbols.length
                  ? 0.3
                  : 0;
                e.add(
                  l.CONCURRENT,
                  new _(_.SHOW_NEW_SYMBOLS_IN_ANIM, null, { delay: t })
                );
              }),
              (o.ShowWinFlow = function (e) {
                var t,
                  n = this.data.getData().gameState,
                  a = n.winSymbols,
                  o = n.totalWinnings,
                  i = n.timesSymbols,
                  S = n.timesUpgrade,
                  d = n.action,
                  w = n.roundWinnings,
                  c =
                    null == (t = this.data.preData.gameState)
                      ? void 0
                      : t.winSymbols.length,
                  p = "freeSpin" == d,
                  E = p ? w : o,
                  m = this.data.getData().parser.newTimesSymbols.length
                    ? 0.8
                    : 0.3,
                  T = c && !a.length && i.length,
                  g = p ? w : o,
                  O = this.data.setBigWinReach(g),
                  I = r.getData().winAmountTime;
                a.length &&
                  (e.add(
                    l.AFTER_PREVIOUS,
                    new _(_.SHOW_WIN_CASH, null, {
                      autoComplete: !0,
                      delay: m,
                    }),
                    new _(
                      _.PLAY_BTM,
                      { url: u.COUNTING },
                      { autoComplete: !0 }
                    ),
                    new _(
                      _.UPDATE_WIN_AMOUNT,
                      { value: E },
                      { autoComplete: !0 }
                    ),
                    new s(
                      s.UPDATE_TOTAL_WINNINGS,
                      { value: o, tweenTime: I },
                      { autoComplete: !0 }
                    ),
                    new _(_.SHOW_SYMBOLS_WIN),
                    new _(_.SHOW_FULL_COMBO),
                    new _(_.REMOVE_SYMBOLS, null, { delay: 0.5 }),
                    new _(_.PLAY_CURRENT_VIEW_FALL_ANIM)
                  ),
                  S.length &&
                    e.add(
                      l.AFTER_PREVIOUS,
                      new _(_.SHOW_TIMES_SYMBOLS_UPGRADE, null, {
                        autoComplete: !0,
                      })
                    )),
                  T &&
                    (O
                      ? e.add(
                          l.AFTER_PREVIOUS,
                          new _(_.SHOW_TIMES_MOVING, null, { delay: 0.8 })
                        )
                      : e.add(
                          l.AFTER_PREVIOUS,
                          new _(_.SHOW_TIMES_MOVING, null, { delay: 0.8 }),
                          new _(
                            _.PLAY_BTM,
                            { url: u.COUNTING },
                            { autoComplete: !0 }
                          ),
                          new s(
                            s.UPDATE_TOTAL_WINNINGS,
                            { value: o, needComplete: !0, tweenTime: I },
                            { autoComplete: !0 }
                          )
                        )),
                  e.add(
                    l.CONCURRENT,
                    new _(_.CREATE_REPLAY_SPIN_COMPLETE_FLOW, null, {
                      autoComplete: !0,
                    })
                  );
              }),
              (o.createEarlySpinFlow = function () {
                if (
                  i.active &&
                  (i.spinsRemaining > 1 || -1 === i.spinsRemaining)
                ) {
                  if (0 !== this.data.getData().gameState.totalWinnings) return;
                  var e = {
                    data: { spinId: this.data.getData().gameState.spinId },
                  };
                  dispatch(_.CREATE_EARLY_SPIN_FLOW, { data: e });
                }
              }),
              n(a, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(S);
                  },
                },
              ]),
              a
            );
          })(o).instance()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/CurrentTimesView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./GameConfigModel.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var e, i, n, a, o, r, s, l, u, m, c, p, f, d, h, T, v, g, A, w;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (i = t.inheritsLoose),
            (n = t.initializerDefineProperty),
            (a = t.assertThisInitialized),
            (o = t.createForOfIteratorHelperLoose),
            (r = t.createClass);
        },
        function (t) {
          (s = t.cclegacy),
            (l = t._decorator),
            (u = t.sp),
            (m = t.v3),
            (c = t.tween),
            (p = t.Vec3),
            (f = t.Node),
            (d = t.Label);
        },
        function (t) {
          h = t.default;
        },
        function (t) {
          T = t.inject;
        },
        function (t) {
          v = t.default;
        },
        function (t) {
          g = t.GameEvent;
        },
        function (t) {
          A = t.EBTM;
        },
        function (t) {
          w = t.default;
        },
      ],
      execute: function () {
        var b, y, _, E, N, G, L, D, F, C, P;
        s._RF.push({}, "2ac1bLFP0hG069nKtxT99g3", "CurrentTimesView", void 0);
        var S = l.ccclass;
        l.property,
          t(
            "CurrentTimesView",
            ((b = S("CurrentTimesView")),
            (y = T("timesNode", f)),
            (_ = T("timesNode/timesAnimation", u.Skeleton)),
            (E = T("timesNode/totalTimes", d)),
            (N = T("timesNode/upgradeAnimation", u.Skeleton)),
            b(
              ((D = e(
                (L = (function (t) {
                  function e() {
                    for (
                      var e, i = arguments.length, o = new Array(i), r = 0;
                      r < i;
                      r++
                    )
                      o[r] = arguments[r];
                    return (
                      (e = t.call.apply(t, [this].concat(o)) || this),
                      n(e, "timesNode", D, a(e)),
                      n(e, "timesAnimation", F, a(e)),
                      n(e, "totalTimes", C, a(e)),
                      n(e, "upgradeAnimation", P, a(e)),
                      (e.lv = 0),
                      (e.breatheTween = null),
                      e
                    );
                  }
                  i(e, t);
                  var s = e.prototype;
                  return (
                    (s.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (s.start = function () {
                      this.init();
                    }),
                    (s.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (s.init = function () {}),
                    (s.setFgElements = function (t) {
                      var e,
                        i = this.data.getData().gameState.currentTimes;
                      if (
                        ((this.timesNode.active = !t),
                        this.timesAnimation.setAnimation(0, "loop_0", !0),
                        (this.lv = 0),
                        null == (e = this.breatheTween) || e.stop(),
                        !t)
                      ) {
                        var n = i <= 0 ? 0 : i;
                        this.updateFGTotalTimes(n);
                      }
                    }),
                    (s.updateFGTotalTimes = function (t) {
                      var e = this,
                        i = [
                          { aniName: "loop_0", lv: 0, maxTimes: 8 },
                          { aniName: "loop_1", lv: 1, maxTimes: 25 },
                          { aniName: "loop_2", lv: 2, maxTimes: 80 },
                        ],
                        n = i[i.length - 1],
                        a = "loop_0",
                        r = 0;
                      if (t >= n.maxTimes) (a = n.aniName), (r = n.lv);
                      else
                        for (var s, l = o(i); !(s = l()).done; ) {
                          var u = s.value;
                          if (t <= u.maxTimes) {
                            (a = u.aniName), (r = u.lv);
                            break;
                          }
                        }
                      if (
                        (r > this.lv &&
                          ((this.upgradeAnimation.node.active = !0),
                          this.upgradeAnimation.setAnimation(0, "lvUp", !1),
                          this.upgradeAnimation.setCompleteListener(
                            function () {
                              e.upgradeAnimation.node.active = !1;
                            }
                          ),
                          dispatch(g.PLAY_BTM, {
                            data: { url: A.TOTAL_TIMES_UPGRADE },
                          }),
                          this.timesAnimation.setAnimation(0, a, !0),
                          this.playBreatheTween(
                            this.totalTimes.node,
                            1 + 0.1 * r
                          )),
                        (this.totalTimes.string = t + "x"),
                        "portrait" == w.getViewModeParam())
                      )
                        if (t.toString().length > 3) {
                          var c = 10 * (t.toString().length - 3);
                          this.totalTimes.node.setPosition(m(-c, 14, 0));
                        } else this.totalTimes.node.setPosition(m(0, 14, 0));
                      this.lv = r;
                    }),
                    (s.playBreatheTween = function (t, e) {
                      var i;
                      null == (i = this.breatheTween) || i.stop(),
                        (this.breatheTween = c(t)
                          .repeatForever(
                            c()
                              .set({ scale: new p(1, 1, 1) })
                              .to(0.6, { scale: new p(e, e, e) })
                              .to(0.6, { scale: new p(1, 1, 1) })
                          )
                          .start());
                    }),
                    (s.reset = function () {}),
                    (s.setData = function (t) {}),
                    (s.show = function () {
                      this.node.active = !0;
                    }),
                    (s.hide = function () {
                      this.node.active = !1;
                    }),
                    (s.addEvents = function () {
                      var t = this;
                      this.on(g.CHANGE_GAME_STYLE, function (e) {
                        t.setFgElements(e.data);
                      }),
                        this.on(g.UPDATE_FG_TOTAL_TIMES, function (e) {
                          t.updateFGTotalTimes(e.data);
                        });
                    }),
                    r(e, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(v);
                        },
                      },
                    ]),
                    e
                  );
                })(h)).prototype,
                "timesNode",
                [y],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (F = e(L.prototype, "timesAnimation", [_], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (C = e(L.prototype, "totalTimes", [E], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (P = e(L.prototype, "upgradeAnimation", [N], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (G = L))
            ) || G)
          );
        s._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/EffectsView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./GameSymbolID.ts",
    "./types.ts",
  ],
  function (t) {
    "use strict";
    var e, o, a, i, n, s, r, l, c, p, u, d, f, h, m;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose), (o = t.createClass);
        },
        function (t) {
          (a = t.cclegacy),
            (i = t._decorator),
            (n = t.instantiate),
            (s = t.ParticleSystem2D),
            (r = t.sp),
            (l = t.tween);
        },
        function (t) {
          c = t.default;
        },
        function (t) {
          (p = t.default), (u = t.EBTM);
        },
        function (t) {
          d = t.default;
        },
        function (t) {
          f = t.GameEvent;
        },
        function (t) {
          h = t.EBackendSymbolID;
        },
        function (t) {
          m = t.EPool;
        },
      ],
      execute: function () {
        var P;
        a._RF.push({}, "042a4ium3dBFrcbHKoOSFN9", "EffectsView", void 0);
        var _ = i.ccclass;
        i.property,
          t(
            "EffectsView",
            _("EffectsView")(
              (P = (function (t) {
                function a() {
                  return t.apply(this, arguments) || this;
                }
                e(a, t);
                var i = a.prototype;
                return (
                  (i.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (i.start = function () {
                    this.init();
                  }),
                  (i.onDestroy = function () {
                    t.prototype.onDestroy.call(this);
                  }),
                  (i.init = function () {
                    this.createFireBallPool();
                  }),
                  (i.createFireBallPool = function () {
                    for (
                      var t = p.getData().filePaths.fireBallPrefab,
                        e = App.cache.get(this.data.module, t).data,
                        o = 0;
                      o < 1;
                      o++
                    ) {
                      var a = n(e);
                      (App.pool.createPool(m.FIREBALL_POOL).cloneNode = a),
                        App.pool.createPool(m.FIREBALL_POOL).put(a);
                    }
                  }),
                  (i.createTimesMovingPool = function () {
                    for (
                      var t = p.getData().filePaths.timesMovingPrefab,
                        e = App.cache.get(this.data.module, t).data,
                        o = 0;
                      o < 1;
                      o++
                    ) {
                      var a = n(e);
                      (a.getComponent(s).autoRemoveOnFinish = !0),
                        (App.pool.createPool(m.TIMES_MOVING_POOL).cloneNode =
                          a),
                        App.pool.createPool(m.TIMES_MOVING_POOL).put(a);
                    }
                  }),
                  (i.createPurpleTimesMovingPool = function () {
                    for (
                      var t = p.getData().filePaths.purpleTimesMovingPrefab,
                        e = App.cache.get(this.data.module, t).data,
                        o = 0;
                      o < 5;
                      o++
                    ) {
                      var a = n(e);
                      (a.getComponent(s).autoRemoveOnFinish = !0),
                        (App.pool.createPool(
                          m.PURPLE_TIMES_MOVING_POOL
                        ).cloneNode = a),
                        App.pool.createPool(m.PURPLE_TIMES_MOVING_POOL).put(a);
                    }
                  }),
                  (i.createBlueTimesMovingPool = function () {
                    for (
                      var t = p.getData().filePaths.blueTimesMovingPrefab,
                        e = App.cache.get(this.data.module, t).data,
                        o = 0;
                      o < 5;
                      o++
                    ) {
                      var a = n(e);
                      (a.getComponent(s).autoRemoveOnFinish = !0),
                        (App.pool.createPool(
                          m.BLUE_TIMES_MOVING_POOL
                        ).cloneNode = a),
                        App.pool.createPool(m.BLUE_TIMES_MOVING_POOL).put(a);
                    }
                  }),
                  (i.showFireBall = function (t, e) {
                    void 0 === e && (e = !1);
                    var o = this.data.getData().symbolPosConfig,
                      a = this.data.getData().parser.newTimesSymbols,
                      i = p.getData().reelConfig.fireBallSpeed,
                      n = App.pool.getPool(m.FIREBALL_POOL).get(),
                      s = n.getComponent(r.Skeleton);
                    if (a.length) {
                      var l = a.find(function (e) {
                          return e.symbolPos == t;
                        }),
                        c = l.isRare ? "fireball_purple" : "fireball_blue",
                        d = l.times >= 100,
                        P = d ? u.FIREBALL_HIT_100X : u.FIREBALL_HIT,
                        _ = d ? 3 : 1,
                        g = l.symbol == h.T1;
                      this.node.addChild(n), (n.position = o.get(t));
                      var v = p.isTurbo;
                      (c = v ? c + "_turbo" : c), (c = e ? c + "_stop" : c);
                      var E = i;
                      v && d && (E = 1.4 * i),
                        (s.timeScale = E),
                        s.setAnimation(0, c, !1),
                        s.setCompleteListener(function () {
                          s.setCompleteListener(null),
                            s.clearTracks(),
                            s.setToSetupPose(),
                            n.removeFromParent(),
                            App.pool.getPool(m.FIREBALL_POOL).put(n);
                        }),
                        g && dispatch(f.SHAKE_NODE, { data: _ }),
                        this.scheduleOnce(function () {
                          dispatch(f.PLAY_BTM, { data: { url: P } });
                        }, 0.3);
                    }
                  }),
                  (i.showTimesMoving = function (t) {
                    var e = this,
                      o = this.data.getData(),
                      a = o.symbolPosConfig,
                      i = o.winBoardPosition,
                      r = o.currentTimesPosition,
                      c = this.data.getData().gameState,
                      d = c.timesSymbols,
                      h = c.currentTimes,
                      m = p.getData().reelConfig.totalTimesFireBallTime;
                    if (h > 0) {
                      var P = p.getData().filePaths.timesMovingPrefab,
                        _ = App.cache.get(this.data.module, P).data,
                        g = n(_);
                      (g.getComponent(s).autoRemoveOnFinish = !0),
                        this.node.addChild(g),
                        (g.position = r),
                        (g.active = !1),
                        l(g)
                          .to(
                            m,
                            { position: i },
                            {
                              onStart: function () {
                                g.active = !0;
                              },
                              onComplete: function () {
                                dispatch(f.EXPAND_WIN_AMOUNT),
                                  dispatch(f.UPDATE_TIMES, { data: h }),
                                  g.destroy();
                              },
                            }
                          )
                          .start(),
                        dispatch(f.PLAY_BTM, { data: { url: u.TIMES_MOVING } });
                    }
                    for (
                      var v = function (o) {
                          var r = d[o].symbolPos,
                            c = p.getData().filePaths,
                            P = c.blueTimesMovingPrefab,
                            _ = c.purpleTimesMovingPrefab,
                            g = d[o].isRare ? _ : P,
                            v = App.cache.get(e.data.module, g).data,
                            E = n(v);
                          E.getComponent(s).autoRemoveOnFinish = !0;
                          var O = h > 0 ? 0.37 * (o + 1) : 0.37 * o;
                          e.node.addChild(E),
                            (E.position = a.get(r)),
                            (E.active = !1),
                            l(E)
                              .delay(O)
                              .to(
                                m,
                                { position: i },
                                {
                                  onStart: function () {
                                    (E.active = !0),
                                      dispatch(f.HIDE_TIMES_LABEL, { data: r }),
                                      dispatch(f.PLAY_TIMES_SYMBOL_FUNCTION, {
                                        data: r,
                                      }),
                                      dispatch(f.PLAY_BTM, {
                                        data: { url: u.TIMES_MOVING },
                                      });
                                  },
                                  onComplete: function () {
                                    var e = d[o].times;
                                    0 != o ||
                                      h > 0 ||
                                      dispatch(f.EXPAND_WIN_AMOUNT),
                                      o == d.length - 1 &&
                                        dispatch(f.MERGE_WIN_AMOUNT, {
                                          data: t,
                                        }),
                                      dispatch(f.UPDATE_TIMES, { data: e }),
                                      E.destroy();
                                  },
                                }
                              )
                              .start();
                        },
                        E = 0;
                      E < d.length;
                      E++
                    )
                      v(E);
                  }),
                  (i.reset = function () {}),
                  (i.setData = function (t) {}),
                  (i.show = function () {
                    this.node.active = !0;
                  }),
                  (i.hide = function () {
                    this.node.active = !1;
                  }),
                  (i.addEvents = function () {
                    var t = this;
                    this.on(f.SHOW_FIRE_BALL, function (e) {
                      t.showFireBall(e.data);
                    }),
                      this.on(f.SHOW_FIRE_BALL_QUICK_STOP, function (e) {
                        t.showFireBall(e.data, !0);
                      }),
                      this.on(f.SHOW_TIMES_MOVING, function (e) {
                        t.showTimesMoving(e.complete);
                      });
                  }),
                  o(a, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(d);
                      },
                    },
                  ]),
                  a
                );
              })(c))
            ) || P
          );
        a._RF.pop();
      },
    };
  }
);

System.register("chunks:///_virtual/FlowIDs.ts", ["cc"], function (_) {
  "use strict";
  var O;
  return {
    setters: [
      function (_) {
        O = _.cclegacy;
      },
    ],
    execute: function () {
      var L;
      _("FlowIDs", void 0),
        O._RF.push({}, "ef0c0deI5FLlYNOqHyX3PsA", "FlowIDs", void 0),
        (function (_) {
          (_.UNKNOWN = "UNKNOWN"),
            (_.SPIN_FLOW = "SPIN_FLOW"),
            (_.STOP_SPIN_FLOW = "STOP_SPIN_FLOW"),
            (_.CLOSE_SPIN_FLOW = "CLOSE_SPIN_FLOW"),
            (_.SPIN_CLOSED_FLOW = "SPIN_CLOSED_FLOW"),
            (_.RESUME_FLOW = "RESUME_FLOW"),
            (_.QUICK_STOP_FLOW = "QUICK_STOP_FLOW"),
            (_.EARLY_SPIN_FLOW = "EARLY_SPIN_FLOW"),
            (_.NEXT_SPIN_FLOW = "NEXT_SPIN_FLOW"),
            (_.SHOW_FG_INTRO_FLOW = "SHOW_FG_INTRO_FLOW"),
            (_.SHOW_FG_SUMMARY_FLOW = "SHOW_FG_SUMMARY_FLOW"),
            (_.EMPTY_SPIN_FLOW = "EMPTY_SPIN_FLOW"),
            (_.QUICK_STOP_EMPTY_FLOW = "QUICK_STOP_EMPTY_FLOW"),
            (_.REPLAY_SPIN_FLOW = "REPLAY_SPIN_FLOW"),
            (_.REPLAY_STOP_SPIN_FLOW = " REPLAY_STOP_SPIN_FLOW"),
            (_.REPLAY_CLOSE_SPIN_FLOW = "REPLAY_CLOSE_SPIN_FLOW"),
            (_.REPLAY_RESUME_FLOW = "REPLAY_RESUME_FLOW"),
            (_.REPLAY_QUICK_STOP_FLOW = "REPLAY_QUICK_STOP_FLOW"),
            (_.REPLAY_NEXT_SPIN_FLOW = "REPLAY_NEXT_SPIN_FLOW"),
            (_.REPLAY_SHOW_FG_INTRO_FLOW = "REPLAY_SHOW_FG_INTRO_FLOW"),
            (_.REPLAY_SHOW_FG_SUMMARY_FLOW = "REPLAY_SHOW_FG_SUMMARY_FLOW");
        })(L || (L = _("FlowIDs", {}))),
        O._RF.pop();
    },
  };
});

System.register(
  "chunks:///_virtual/FreeGameAlertView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./UIView.ts",
    "./Decorators.ts",
    "./MisaButton.ts",
    "./CmmSlotUtils.ts",
    "./LoadUtils.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./AutoPlayModel.ts",
    "./ReplayModel.ts",
    "./PlatformModel.ts",
    "./SlotFrameworkEvent.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var e,
      i,
      a,
      n,
      s,
      r,
      o,
      l,
      c,
      f,
      u,
      h,
      p,
      d,
      _,
      E,
      g,
      m,
      S,
      G,
      A,
      F,
      T,
      b,
      M,
      B,
      I,
      C,
      N,
      D,
      R,
      y;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (i = t.inheritsLoose),
            (a = t.initializerDefineProperty),
            (n = t.assertThisInitialized),
            (s = t.createClass);
        },
        function (t) {
          (r = t.cclegacy),
            (o = t._decorator),
            (l = t.sp),
            (c = t.tween),
            (f = t.Vec3),
            (u = t.NodeEventType),
            (h = t.KeyCode),
            (p = t.Node),
            (d = t.Sprite),
            (_ = t.Label);
        },
        function (t) {
          E = t.EBundles;
        },
        function (t) {
          g = t.default;
        },
        function (t) {
          m = t.inject;
        },
        function (t) {
          S = t.default;
        },
        function (t) {
          G = t.CmmSlotUtils;
        },
        function (t) {
          A = t.LoadUtils;
        },
        function (t) {
          (F = t.default), (T = t.EBTM), (b = t.EBGM);
        },
        function (t) {
          M = t.default;
        },
        function (t) {
          B = t.GameEvent;
        },
        function (t) {
          I = t.EGameType;
        },
        function (t) {
          C = t.default;
        },
        function (t) {
          N = t.default;
        },
        function (t) {
          D = t.default;
        },
        function (t) {
          R = t.SlotFrameworkEvent;
        },
        function (t) {
          y = t.default;
        },
      ],
      execute: function () {
        var L, O, w, v, U, P, H, k, V, z, Y, W, K, j, x, q, J;
        r._RF.push({}, "6f2f7J7gBdOCbjMUnUyZQqI", "FreeGameAlertView", void 0);
        var Q,
          Z = o.ccclass;
        o.property;
        !(function (t) {
          (t[(t.NONE = 0)] = "NONE"),
            (t[(t.START_FREE_GAME = 1)] = "START_FREE_GAME"),
            (t[(t.START_FREE_GAME_END = 2)] = "START_FREE_GAME_END"),
            (t[(t.FINISH_FREE_GAME = 3)] = "FINISH_FREE_GAME"),
            (t[(t.FINISH_FREE_GAME_END = 4)] = "FINISH_FREE_GAME_END");
        })(Q || (Q = {}));
        t(
          "FreeGameAlertView",
          ((L = Z("FreeGameAlertView")),
          (O = m("alert", p)),
          (w = m("alert/bbr", p)),
          (v = m("alert/effectBg", l.Skeleton)),
          (U = m("alert/fgFontSprite", d)),
          (P = m("alert/fgTimes", _)),
          (H = m("alert/startBtn", p)),
          (k = m("alert/finishBtn", p)),
          L(
            ((Y = e(
              (z = (function (t) {
                function e() {
                  for (
                    var e, i = arguments.length, s = new Array(i), r = 0;
                    r < i;
                    r++
                  )
                    s[r] = arguments[r];
                  return (
                    (e = t.call.apply(t, [this].concat(s)) || this),
                    a(e, "alert", Y, n(e)),
                    a(e, "bbr", W, n(e)),
                    a(e, "effectBg", K, n(e)),
                    a(e, "fgFontSprite", j, n(e)),
                    a(e, "fgTimes", x, n(e)),
                    a(e, "startBtn", q, n(e)),
                    a(e, "finishBtn", J, n(e)),
                    (e.finishFGCallback = null),
                    (e.freeGameAlertStatus = Q.NONE),
                    e
                  );
                }
                i(e, t);
                var r = e.prototype;
                return (
                  (r.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (r.start = function () {
                    this.init();
                  }),
                  (r.onDestroy = function () {
                    t.prototype.onDestroy.call(this);
                  }),
                  (e.getPrefabUrl = function () {
                    return "prefabs/" + y.getViewModeParam() + "/FGAlertView";
                  }),
                  (r.init = function () {
                    (this.enabledKeyDown = !0), this.setStartCloseBtnLocalize();
                  }),
                  (r.goToFreeGame = function () {
                    var t = this,
                      e = null;
                    if (
                      (dispatch(R.HIDE_SPIN_BAR),
                      this.data.getData().newGameState &&
                        this.data.getData().newGameState.length &&
                        this.data.getData().newGameState.length > 0)
                    ) {
                      e = this.data.getData().spinId;
                      dispatch(B.SHOW_TRANSITION_IN, {
                        data: function () {
                          (t.data.currentGameType = I.FREE_GAME),
                            dispatch(B.CHANGE_GAME_STYLE, { data: !1 }),
                            dispatch(B.PLAY_BGM, { data: b.FREEGAME }),
                            N.isReplay
                              ? t.scheduleOnce(function () {
                                  dispatch(B.CREATE_REPLAY_SPIN_FLOW, {
                                    data: { spinId: e, cheat: null },
                                  });
                                }, 1)
                              : t.scheduleOnce(function () {
                                  dispatch(B.CREATE_SPIN_FLOW, {
                                    data: { spinId: e, next: !0, cheat: null },
                                  });
                                }, 1);
                        },
                      });
                    } else {
                      e = this.data.getData().gameState.spinId;
                      dispatch(B.SHOW_TRANSITION_IN, {
                        data: function () {
                          (t.data.currentGameType = I.FREE_GAME),
                            dispatch(B.CHANGE_GAME_STYLE, { data: !1 }),
                            dispatch(B.PLAY_BGM, { data: b.FREEGAME }),
                            N.isReplay
                              ? t.scheduleOnce(function () {
                                  dispatch(B.CREATE_REPLAY_SPIN_FLOW, {
                                    data: { spinId: e, cheat: null },
                                  });
                                }, 1)
                              : t.scheduleOnce(function () {
                                  dispatch(B.CREATE_SPIN_FLOW, {
                                    data: { spinId: e, cheat: null },
                                  });
                                }, 1);
                        },
                      });
                    }
                  }),
                  (r.goToMainGame = function () {
                    var t = this;
                    dispatch(B.SHOW_TRANSITION_OUT, {
                      data: function () {
                        (t.data.currentGameType = I.MAIN_GAME),
                          dispatch(B.CHANGE_GAME_STYLE, { data: !0 }),
                          dispatch(B.PLAY_BGM, { data: b.MAINGAME }),
                          dispatch(R.SHOW_SPIN_BAR);
                      },
                    });
                  }),
                  (r.startFreeGame = function () {
                    (this.startBtn.active = !1),
                      (this.alert.active = !1),
                      this.goToFreeGame(),
                      (this.data.originTurbo = F.isTurbo),
                      F.setIsTurbo(!1, !1),
                      this.unschedule(this.startFreeGame),
                      this.bbr.targetOff(this),
                      this.close();
                  }),
                  (r.finishFreeGame = function () {
                    (this.finishBtn.active = !1),
                      (this.alert.active = !1),
                      F.stopOnFg && (C.active = !1),
                      this.goToMainGame(),
                      F.setIsTurbo(
                        this.data.originTurbo
                          ? this.data.originTurbo
                          : F.isTurbo,
                        !1
                      ),
                      this.unschedule(this.finishFreeGame),
                      this.bbr.targetOff(this),
                      this.close();
                  }),
                  (r.playBounceTween = function (t, e) {
                    c(t)
                      .delay(0.2)
                      .to(0.1, { scale: new f(0.9, 0.9, 0.9) })
                      .to(
                        0.2,
                        { scale: new f(0.6, 0.6, 0.6) },
                        {
                          onComplete: function () {
                            e && e();
                          },
                        }
                      )
                      .start();
                  }),
                  (r.setStartCloseBtnLocalize = function () {
                    var t = F.getData().filePaths.localeSpriteFrame;
                    (this.startBtn.getComponent(S).customNormalSprite =
                      A.getDirSp(E[E.g1001], t, "t_font_01_normal")),
                      (this.startBtn.getComponent(S).customPressedSprite =
                        A.getDirSp(E[E.g1001], t, "t_font_01_pressed")),
                      (this.startBtn.getComponent(S).customHoverSprite =
                        A.getDirSp(E[E.g1001], t, "t_font_01_pressed")),
                      (this.startBtn.getComponent(S).customDisabledSprite =
                        A.getDirSp(E[E.g1001], t, "t_font_01_disabled")),
                      (this.finishBtn.getComponent(S).customNormalSprite =
                        A.getDirSp(E[E.g1001], t, "t_font_02_normal")),
                      (this.finishBtn.getComponent(S).customPressedSprite =
                        A.getDirSp(E[E.g1001], t, "t_font_02_pressed")),
                      (this.finishBtn.getComponent(S).customHoverSprite =
                        A.getDirSp(E[E.g1001], t, "t_font_02_pressed")),
                      (this.finishBtn.getComponent(S).customDisabledSprite =
                        A.getDirSp(E[E.g1001], t, "t_font_02_disabled"));
                  }),
                  (r.showIntroAlert = function () {
                    var t = this,
                      e = this.data.getData().gameState,
                      i = F.getData().autoCloseTime;
                    dispatch(B.MUSIC_VOLUME_MULTIPLE, { data: 0.5 }),
                      (this.alert.active = !0),
                      (this.finishBtn.active = !1),
                      (this.fgTimes.string = e.freeGameCount.toString()),
                      this.fgTimes.node.position.set(0, 225, 0),
                      (this.fgFontSprite.spriteFrame =
                        this.data.getLocaleSpriteFrame("t_font_03")),
                      this.fgFontSprite.node.position.set(0, 22, 0),
                      this.playBounceTween(this.fgFontSprite.node),
                      (this.effectBg.skeletonData =
                        this.data.getGameAlertSpine("f_spins_bg")),
                      this.effectBg.setAnimation(0, "in", !1),
                      this.effectBg.setCompleteListener(function () {
                        dispatch(B.MUSIC_VOLUME_MULTIPLE, { data: 2 }),
                          t.effectBg.setAnimation(0, "loop", !0),
                          (t.startBtn.active = !0),
                          i && t.scheduleOnce(t.startFreeGame, i),
                          t.bbr.once(u.TOUCH_END, t.startFreeGame, t),
                          t.startBtn.once(u.TOUCH_END, t.startFreeGame, t),
                          t.effectBg.setCompleteListener(null);
                      }),
                      this.schedule(function () {
                        t.freeGameAlertStatus = Q.START_FREE_GAME;
                      }, 0.5),
                      dispatch(B.PLAY_BTM, { data: { url: T.FREEGAME_IN } });
                  }),
                  (r.showSummaryAlert = function (t) {
                    var e = this,
                      i = this.data.getData().gameState.totalWinnings,
                      a = F.getData().autoCloseTime;
                    dispatch(B.MUSIC_VOLUME_MULTIPLE, { data: 0.2 }),
                      (this.alert.active = !0),
                      (this.startBtn.active = !1),
                      (this.fgTimes.string = G.formatNumber(i)),
                      this.fgTimes.node.position.set(0, 32, 0);
                    var n = "t_font_04";
                    D.getData().theme &&
                      "xin-star" == D.getData().theme &&
                      (n += "_01"),
                      (this.fgFontSprite.spriteFrame =
                        this.data.getLocaleSpriteFrame(n)),
                      this.fgFontSprite.node.position.set(0, 148, 0),
                      this.playBounceTween(this.fgFontSprite.node),
                      (this.effectBg.skeletonData =
                        this.data.getGameAlertSpine("f_total_bg")),
                      this.effectBg.setAnimation(0, "in", !1),
                      this.effectBg.setCompleteListener(function () {
                        e.effectBg.setAnimation(0, "loop", !0),
                          (e.finishBtn.active = !0),
                          (e.finishFGCallback = function () {
                            e.finishFreeGame(),
                              e.unschedule(e.finishFGCallback),
                              dispatch(B.MUSIC_VOLUME_MULTIPLE, { data: 5 }),
                              t();
                          }),
                          a && e.scheduleOnce(e.finishFGCallback, a),
                          e.bbr.once(u.TOUCH_END, e.finishFGCallback, e),
                          e.finishBtn.once(u.TOUCH_END, e.finishFGCallback, e),
                          e.effectBg.setCompleteListener(null);
                      }),
                      this.schedule(function () {
                        e.freeGameAlertStatus = Q.FINISH_FREE_GAME;
                      }, 0.5),
                      dispatch(B.PLAY_BTM, { data: { url: T.FREEGAME_OUT } });
                  }),
                  (r.onKeyDown = function (e) {
                    if (
                      (t.prototype.onKeyDown.call(this, e),
                      e.keyCode === h.SPACE)
                    )
                      switch (this.freeGameAlertStatus) {
                        case Q.START_FREE_GAME:
                          this.startFreeGame(),
                            (this.freeGameAlertStatus = Q.START_FREE_GAME_END);
                          break;
                        case Q.FINISH_FREE_GAME:
                          null != this.finishFGCallback &&
                            (this.finishFGCallback && this.finishFGCallback(),
                            (this.freeGameAlertStatus =
                              Q.FINISH_FREE_GAME_END));
                      }
                  }),
                  s(e, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(M);
                      },
                    },
                  ]),
                  e
                );
              })(g)).prototype,
              "alert",
              [O],
              {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              }
            )),
            (W = e(z.prototype, "bbr", [w], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (K = e(z.prototype, "effectBg", [v], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (j = e(z.prototype, "fgFontSprite", [U], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (x = e(z.prototype, "fgTimes", [P], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (q = e(z.prototype, "startBtn", [H], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (J = e(z.prototype, "finishBtn", [k], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (V = z))
          ) || V)
        );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/FullComboView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./GameConfigModel.ts",
  ],
  function (t) {
    "use strict";
    var e, n, i, o, a, r, c, l, s, u, f, p, h, y, d, m;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (n = t.inheritsLoose),
            (i = t.initializerDefineProperty),
            (o = t.assertThisInitialized),
            (a = t.createClass);
        },
        function (t) {
          (r = t.cclegacy),
            (c = t._decorator),
            (l = t.sp),
            (s = t.tween),
            (u = t.Node),
            (f = t.UIOpacityComponent);
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          h = t.inject;
        },
        function (t) {
          y = t.default;
        },
        function (t) {
          d = t.GameEvent;
        },
        function (t) {
          m = t.EBTM;
        },
      ],
      execute: function () {
        var b, v, C, w, O, g, F, L, A;
        r._RF.push({}, "341b72SbZpJSpWKWhsOPrMz", "FullComboView", void 0);
        var D = c.ccclass;
        c.property,
          t(
            "FullComboView",
            ((b = D("FullComboView")),
            (v = h("alert", u)),
            (C = h("alert", f)),
            (w = h("alert/effect", l.Skeleton)),
            b(
              ((F = e(
                (g = (function (t) {
                  function e() {
                    for (
                      var e, n = arguments.length, a = new Array(n), r = 0;
                      r < n;
                      r++
                    )
                      a[r] = arguments[r];
                    return (
                      (e = t.call.apply(t, [this].concat(a)) || this),
                      i(e, "alert", F, o(e)),
                      i(e, "alertOpacity", L, o(e)),
                      i(e, "effect", A, o(e)),
                      e
                    );
                  }
                  n(e, t);
                  var r = e.prototype;
                  return (
                    (r.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (r.start = function () {
                      this.init();
                    }),
                    (r.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (r.init = function () {}),
                    (r.showFullCombo = function (t) {
                      var e = this;
                      this.data.getData().parser.isFullCombo
                        ? (this.openAlert(),
                          this.effect.setAnimation(0, "in", !1),
                          this.effect.setCompleteListener(function () {
                            e.effect.setAnimation(0, "loop", !0);
                          }),
                          dispatch(d.PLAY_BTM, { data: { url: m.FULLCOMBO } }),
                          this.scheduleOnce(function () {
                            e.closeAlert(function () {
                              t && t();
                            });
                          }, 3))
                        : t && t();
                    }),
                    (r.openAlert = function () {
                      (this.alert.active = !0),
                        s(this.alertOpacity).to(1, { opacity: 255 }).start();
                    }),
                    (r.closeAlert = function (t) {
                      var e = this;
                      s(this.alertOpacity)
                        .to(0.3, { opacity: 0 })
                        .call(function () {
                          (e.alert.active = !1), t && t();
                        })
                        .start();
                    }),
                    (r.reset = function () {}),
                    (r.setData = function (t) {}),
                    (r.show = function () {
                      this.node.active = !0;
                    }),
                    (r.hide = function () {
                      this.node.active = !1;
                    }),
                    (r.addEvents = function () {
                      var t = this;
                      this.on(d.SHOW_FULL_COMBO, function (e) {
                        t.showFullCombo(e.complete);
                      });
                    }),
                    a(e, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(y);
                        },
                      },
                    ]),
                    e
                  );
                })(p)).prototype,
                "alert",
                [v],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (L = e(g.prototype, "alertOpacity", [C], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (A = e(g.prototype, "effect", [w], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (O = g))
            ) || O)
          );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/g1001",
  [
    "./GameEntry.ts",
    "./ParseResponse.ts",
    "./RegisterNewCommands.ts",
    "./CreateReplayCloseSpinFlowCmd.ts",
    "./CreateReplayFlow.ts",
    "./CreateReplayQuickStopFlowCmd.ts",
    "./CreateReplaySpinCompleteFlowCmd.ts",
    "./CreateReplaySpinFlowCmd.ts",
    "./CreateReplayStopSpinFlowCmd.ts",
    "./FlowIDs.ts",
    "./CreateNewCloseSpinFlowCmd.ts",
    "./CreateNewEarlySpinFlowCmd.ts",
    "./CreateNewQuickStopFlowCmd.ts",
    "./CreateNewResumeFlowCmd.ts",
    "./CreateNewSpinCompleteFlowCmd.ts",
    "./CreateNewSpinFlowCmd.ts",
    "./CreateNewStopSpinFlowCmd.ts",
    "./NewSpinClosedCmd.ts",
    "./StaticData.ts",
    "./StaticFakeCmd.ts",
    "./BuyFeatureButton.ts",
    "./Symbol.ts",
    "./BackgroundView.ts",
    "./BigwinView.ts",
    "./BuyFeatureView.ts",
    "./CharacterView.ts",
    "./CurrentTimesView.ts",
    "./EffectsView.ts",
    "./FreeGameAlertView.ts",
    "./FullComboView.ts",
    "./IntroView.ts",
    "./JackpotView.ts",
    "./PrizeView.ts",
    "./ReelView.ts",
    "./ReplayUIViewL.ts",
    "./ReplayUIViewP.ts",
    "./SymbolView.ts",
    "./TransitionView.ts",
    "./TreasuresView.ts",
    "./WinView.ts",
    "./GameColor.ts",
    "./GameColors.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameLanguage.ts",
    "./GameLanguages.ts",
    "./GameSymbolID.ts",
    "./GlobalModel.ts",
    "./GameEvent.ts",
    "./GameLogic.ts",
    "./GameHandler.ts",
    "./GameSender.ts",
    "./GameService.ts",
    "./res-type2.ts",
    "./types.ts",
    "./GameView.ts",
  ],
  function () {
    "use strict";
    return {
      setters: [
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
      ],
      execute: function () {},
    };
  }
);

System.register(
  "chunks:///_virtual/GameColor.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./ColorProxy.ts",
    "./GameData.ts",
    "./GameColors.ts",
  ],
  function (o) {
    "use strict";
    var t, n, r, e, c, i;
    return {
      setters: [
        function (o) {
          t = o.inheritsLoose;
        },
        function (o) {
          n = o.cclegacy;
        },
        function (o) {
          (r = o.injectColorData), (e = o.ColorProxy);
        },
        function (o) {
          c = o.default;
        },
        function (o) {
          i = o;
        },
      ],
      execute: function () {
        var u;
        n._RF.push({}, "629c30HIo5Nhq6hjcenLB96", "GameColor", void 0);
        o(
          "GameColor",
          r(
            (u = (function (o) {
              function n() {
                for (
                  var t, n = arguments.length, r = new Array(n), e = 0;
                  e < n;
                  e++
                )
                  r[e] = arguments[e];
                return (
                  ((t = o.call.apply(o, [this].concat(r)) || this).bundle =
                    c.module),
                  t
                );
              }
              return (
                t(n, o),
                (n.prototype.init = function () {
                  this.importColors(i);
                }),
                n
              );
            })(e))
          ) || u
        );
        n._RF.pop();
      },
    };
  }
);

System.register("chunks:///_virtual/GameColors.ts", ["cc"], function (e) {
  "use strict";
  var n, r;
  return {
    setters: [
      function (e) {
        (n = e.cclegacy), (r = e.Color);
      },
    ],
    execute: function () {
      e("EUiColorKeys", void 0),
        n._RF.push({}, "0634fr/0LRCLKiPsQwyOy3p", "GameColors", void 0);
      var a,
        o = e("DARK", {
          mode: "dark",
          data: {
            mainGame: {
              auxiliary: new r("#4e3487"),
              main: new r("#ab84ff"),
              mainHover: new r("#896acc"),
              topbar: new r(42, 26, 77, 209.1),
            },
            record: {
              5: new r(255, 255, 255, 12.75),
              10: new r(255, 255, 255, 255 * 0.24),
            },
            background: {
              0: new r("#c9c9cc"),
              20: new r("#a9a9ad"),
              40: new r("#88898e"),
              60: new r("#68696f"),
              80: new r("#474951"),
              100: new r("#272932"),
            },
            white: {
              info01: new r("#ffffff"),
              default01: new r(255, 255, 255, 38.25),
              default02: new r(255, 255, 255, 255 * 0.24),
              hover01: new r(255, 255, 255, 76.5),
              hover02: new r(255, 255, 255, 255 * 0.08),
              labelDefault01: new r(255, 255, 255, 153),
              textAuto01: new r("#ffffff"),
            },
            red: { primary: new r("#ff6433") },
            green: { primary: new r("#3ae300") },
            yellow: {
              primary: new r("#ffd680"),
              secondary: new r(255, 168, 0, 76.5),
            },
          },
        }).data;
      a || (a = e("EUiColorKeys", {}));
      var f = {};
      for (var t in o)
        for (var w in o[t]) {
          var i = c(t + "_" + w);
          f[i] && Log.e("碰撞檢測: " + t + "_" + w + " 的哈希碰撞"),
            (f[i] = t + "_" + w),
            (a[t + "_" + w] = i);
        }
      function c(e) {
        for (var n = 0, r = 0; r < e.length; r++) {
          (n = (n << 5) - n + e.charCodeAt(r)), (n |= 0);
        }
        return n;
      }
      n._RF.pop();
    },
  };
});

System.register(
  "chunks:///_virtual/GameConfigModel.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./ObjectUtils.ts",
    "./BaseModel.ts",
    "./DefinitionModel.ts",
    "./SettingsModel.ts",
    "./GameSender.ts",
    "./GameData.ts",
    "./UrlModel.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var s, e, a, i, m, _, o, n, b, u, r;
    return {
      setters: [
        function (t) {
          (s = t.inheritsLoose), (e = t.createClass);
        },
        function (t) {
          a = t.cclegacy;
        },
        function (t) {
          i = t.ObjectUtils;
        },
        function (t) {
          m = t.BaseModel;
        },
        function (t) {
          _ = t.default;
        },
        function (t) {
          o = t.default;
        },
        function (t) {
          n = t.GameSender;
        },
        function (t) {
          b = t.default;
        },
        function (t) {
          u = t.default;
        },
        function (t) {
          r = t.default;
        },
      ],
      execute: function () {
        var l, c;
        t({ EBGM: void 0, EBTM: void 0 }),
          a._RF.push({}, "bc736HyOmlPLp6pSG1muxbh", "GameConfigModel", void 0),
          (function (t) {
            (t.MAINGAME = "assets/music/bgm/bgm_mg"),
              (t.FREEGAME = "assets/music/bgm/bgm_fg");
          })(l || (l = t("EBGM", {}))),
          (function (t) {
            (t.SPIN = "assets/music/btm/btm_spin"),
              (t.CH_LOOP = "assets/music/btm/btm_ch_loop"),
              (t.FREEGAME_IN = "assets/music/btm/btm_fg_in"),
              (t.FREEGAME_OUT = "assets/music/btm/btm_fg_out"),
              (t.SYMBOL_WIN = "assets/music/btm/btm_fx_symbol_frame"),
              (t.SYMBOL_BREAK = "assets/music/btm/btm_fx_symbol_out"),
              (t.TIMES_SYMBOL_01 = "assets/music/btm/btm_muti_function_1"),
              (t.TIMES_SYMBOL_02 = "assets/music/btm/btm_muti_function_2"),
              (t.SYMBOL_TURBO_FALL_OUT = "assets/music/btm/btm_fall_auto_1"),
              (t.SYMBOL_TURBO_FALL_IN = "assets/music/btm/btm_fall_auto_2"),
              (t.SYMBOL_NORMAL_FALL_OUT = "assets/music/btm/btm_fall_normal_1"),
              (t.SYMBOL_NORMAL_FALL_IN = "assets/music/btm/btm_fall_normal_2"),
              (t.FIREBALL_IN = "assets/music/btm/btm_fx_symbol_function_1"),
              (t.FIREBALL_HIT = "assets/music/btm/btm_fx_symbol_function_2"),
              (t.FIREBALL_HIT_100X =
                "assets/music/btm/btm_fx_symbol_function_2_100x"),
              (t.CH_MAN_TRANSITION = "assets/music/btm/btm_ch_male"),
              (t.CH_WOMAN_TRANSITION = "assets/music/btm/btm_ch_female"),
              (t.SMALL_PRIZE_IN = "assets/music/btm/btm_w_in_prize_s"),
              (t.ULTRA_IN = "assets/music/btm/btm_w_ultra"),
              (t.LEGEND_IN = "assets/music/btm/btm_w_legend"),
              (t.WIN_LOOP = "assets/music/btm/btm_w_loop"),
              (t.S_PRIZE_LOOP = "assets/music/btm/btm_w_loop_prize_s"),
              (t.L_PRIZE_LOOP = "assets/music/btm/btm_w_loop_prize_l"),
              (t.JP_WIN = "assets/music/btm/btm_w_jp"),
              (t.FULLCOMBO = "assets/music/btm/btm_fc"),
              (t.SCATTER_IN = "assets/music/btm/btm_scatter_in"),
              (t.SCATTER_IN_X2 = "assets/music/btm/btm_scatter_in_x2"),
              (t.SCATTER_WIN = "assets/music/btm/btm_scatter_win"),
              (t.TIMES_SYMBOL_UPGRADE = "assets/music/btm/btm_muti_upgrade"),
              (t.TIMES_MOVING = "assets/music/btm/btm_muti_total"),
              (t.TOTAL_TIMES_UPGRADE =
                "assets/music/btm/btm_totalTimes_upgrade"),
              (t.TRANSITION = "assets/music/btm/btm_transitions"),
              (t.SCORE = "assets/music/btm/btm_score"),
              (t.SCORE_PLUS = "assets/music/btm/btm_score_plus"),
              (t.FIREWORKS = "assets/music/btm/btm_w_fireworks"),
              (t.COUNTING = "assets/music/btm/btm_counting"),
              (t.OPEN_FEATURE = "assets/music/btm/btm_open"),
              (t.CLOSE_FEATURE = "assets/music/btm/btm_close"),
              (t.JACKPOT_WIN = "assets/music/btm/btm_w_jp_line"),
              (t.JP_POPUP_IN_1 = "assets/music/btm/btm_w_jp_intro_1"),
              (t.JP_POPUP_IN_2 = "assets/music/btm/btm_w_jp_intro_2"),
              (t.JP_POPUP_LOOP_1 = "assets/music/btm/btm_w_jp_loop_1"),
              (t.JP_POPUP_LOOP_2 = "assets/music/btm/btm_w_jp_loop_2"),
              (t.JP_MINI_VOCAL = "assets/music/btm/btm_w_jp_mini_vocal"),
              (t.JP_MINOR_VOCAL = "assets/music/btm/btm_w_jp_minor_vocal"),
              (t.JP_MAJOR_VOCAL = "assets/music/btm/btm_w_major_vocal"),
              (t.JP_GRAND_VOCAL = "assets/music/btm/btm_w_grand_vocal"),
              (t.BIG_VOCAL = "assets/music/btm/btm_w_big_vocal"),
              (t.SUPER_VOCAL = "assets/music/btm/btm_w_super_vocal"),
              (t.MEGA_VOCAL = "assets/music/btm/btm_w_mega_vocal"),
              (t.ULTRA_VOCAL = "assets/music/btm/btm_w_ultra_vocal"),
              (t.LEGENDARY_VOCAL = "assets/music/btm/btm_w_legendary_vocal");
          })(c || (c = t("EBTM", {})));
        var f = (function (t) {
          function a() {
            var s;
            ((s = t.call(this) || this).turboMode = {
              animStagger: 0,
              speed: 0.16,
              characterFireSpeed: 2.5,
              fireBallSpeed: 3.2,
              totalTimesFireBallTime: 0.5,
            }),
              (s.normalMode = {
                animStagger: 0.03,
                speed: 0.23,
                characterFireSpeed: 1.4,
                fireBallSpeed: 1.85,
                totalTimesFireBallTime: 0.5,
              }),
              (s._isTurbo = !1),
              (s.canQuickStop = !1),
              (s.quickStopCount = 0),
              (s.canQuickStopEarlySpin = !1),
              (s.useProEffect = !1),
              (s.stopOnBigwinPrize = !1),
              (s.stopOnJpPrize = !0),
              (s.stopOnFg = !0);
            var e = u.getLanguageParam(),
              a = r.getViewModeParam();
            return (
              (s.data = {
                reelConfig: s.normalMode,
                filePaths: {
                  symbolsSpriteFrame: "assets/texture/symbols/" + a,
                  symbolsSpriteFrameBlur: "assets/texture/symbolsBlur/" + a,
                  symbolsAtlas: "assets/atlas/symbols/" + a + "/symbols",
                  symbolsBlurAtlas:
                    "assets/atlas/symbolsBlur/" + a + "/symbolsBlur",
                  common: "assets/texture/common/" + a,
                  localeSpriteFrame: "assets/texture/locale/" + a + "/" + e,
                  font: "assets/font/" + a,
                  gameAlertsSkeletonData: "assets/spine/" + a + "/prize",
                  spinSkeleton: "assets/spine/" + a + "/spin",
                  transitionsSkeletonData: "assets/spine/" + a + "/transition",
                  symbolsSkeletonData: "assets/spine/" + a + "/symbol",
                  symbolPrefab: "prefabs/" + a + "/Symbol",
                  winCashPrefab: "prefabs/" + a + "/WinCash",
                  fireBallPrefab: "prefabs/" + a + "/Fireball",
                  timesMovingPrefab: "prefabs/" + a + "/TimesMoving",
                  blueTimesMovingPrefab: "prefabs/" + a + "/BlueTimesMoving",
                  purpleTimesMovingPrefab:
                    "prefabs/" + a + "/PurpleTimesMoving",
                  buyFeatureBtnPrefab: "prefabs/" + a + "/BuyFeatureButton",
                  introSkeleton: "assets/spine/intro",
                },
                bigwinAutoCloseTime: 5,
                hasTimesSymbolsDelay: 0.35,
                nextSpinDelay: 0,
                symbolQuickInTime: 0.16,
                winAmountTime: 1.75,
                autoCloseTime: null,
              }),
              s
            );
          }
          s(a, t),
            (a.Instance = function () {
              return this._instance || (this._instance = new a());
            });
          var m = a.prototype;
          return (
            (m.setData = function (t) {
              this.setIsTurbo(
                t.platform.player.settings.advancedSettings.turbo
              ),
                (App.dataCenter.get(b).originTurbo =
                  t.platform.player.settings.advancedSettings.turbo);
              var s = _.getData(),
                e = s.autoConfirmTime,
                a = s.autoSpinInterval;
              (this.data.reelConfig = this.isTurbo
                ? this.turboMode
                : this.normalMode),
                (this.data.autoCloseTime = e),
                (this.data.nextSpinDelay = a),
                (this.data.hasTimesSymbolsDelay = a),
                (this.data.bigwinAutoCloseTime =
                  t.engine.definition.prizeAutoNextDelay);
            }),
            (m.setNewData = function (t) {
              this.setIsTurbo(
                t.platform.player.settings.advancedSettings.turbo
              ),
                (App.dataCenter.get(b).originTurbo =
                  t.platform.player.settings.advancedSettings.turbo);
              var s = _.getData(),
                e = s.autoConfirmTime,
                a = s.autoSpinInterval;
              (this.data.reelConfig = this.isTurbo
                ? this.turboMode
                : this.normalMode),
                (this.data.autoCloseTime = e),
                (this.data.nextSpinDelay = a),
                (this.data.hasTimesSymbolsDelay = a),
                (this.data.bigwinAutoCloseTime =
                  t.engine.definition.prizeAutoNextDelay);
            }),
            (m.sendSettingByTurbo = function () {
              var t = { turbo: o.turbo },
                s = { turbo: this.isTurbo },
                e = i.diffObjects(t, s);
              if (Object.keys(e).length > 0) {
                var a = { type: "game", data: e };
                App.senderManager.get(n).setting(a);
              }
              o.turbo = this.isTurbo;
            }),
            (m.setIsTurbo = function (t, s) {
              void 0 === s && (s = !0),
                (this._isTurbo = t),
                (this.data.reelConfig = this.isTurbo
                  ? this.turboMode
                  : this.normalMode),
                s && this.sendSettingByTurbo();
            }),
            e(a, [
              {
                key: "isTurbo",
                get: function () {
                  return this._isTurbo;
                },
              },
            ]),
            a
          );
        })(m);
        f._instance = null;
        t("default", f.Instance());
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameData.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./MathUtil.ts",
    "./GameDataBase.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./GameConfigModel.ts",
    "./GameSymbolID.ts",
    "./AutoPlayModel.ts",
    "./ObjectUtils.ts",
    "./PlatformModel.ts",
    "./StakeModel.ts",
    "./DefinitionModel.ts",
    "./UrlUtils.ts",
    "./LoadUtils.ts",
  ],
  function (t) {
    "use strict";
    var e, a, i, n, s, r, o, l, u, d, h, p, m, c, g, f, y, S, w;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose), (a = t.extends), (i = t.createClass);
        },
        function (t) {
          (n = t.cclegacy), (s = t.v3);
        },
        function (t) {
          r = t.EBundles;
        },
        function (t) {
          o = t.default;
        },
        function (t) {
          l = t.GameDataBase;
        },
        function (t) {
          u = t.GameEvent;
        },
        function (t) {
          d = t.EGameType;
        },
        function (t) {
          h = t.default;
        },
        function (t) {
          p = t.GameSymbolID;
        },
        function (t) {
          m = t.default;
        },
        function (t) {
          c = t.ObjectUtils;
        },
        function (t) {
          g = t.default;
        },
        function (t) {
          f = t.default;
        },
        function (t) {
          y = t.default;
        },
        function (t) {
          S = t.default;
        },
        function (t) {
          w = t.LoadUtils;
        },
      ],
      execute: function () {
        var D;
        t("EInitName", void 0),
          n._RF.push({}, "836b2BI+eNNy5S6Ra47b1+o", "GameData", void 0),
          (function (t) {
            (t.INIT_GAME = "init_game"), (t.INIT_REPLAY = "init_replay");
          })(D || (D = t("EInitName", {}))),
          (t(
            "default",
            (function (t) {
              function n() {
                for (
                  var e, a = arguments.length, i = new Array(a), n = 0;
                  n < a;
                  n++
                )
                  i[n] = arguments[n];
                return (
                  ((e =
                    t.call.apply(t, [this].concat(i)) || this).GAME_VERSION =
                    "3.4.28_4"),
                  (e.preData = void 0),
                  (e._currentGameType = void 0),
                  (e.previousGameType = void 0),
                  (e.originTurbo = null),
                  (e.currSpinIndex = 0),
                  (e.preSpinData = null),
                  (e.isEarlyFlag = !1),
                  (e.isOpenEarlyFlag = !1),
                  (e.isSendOutEarlyFlag = !1),
                  (e.earlySpinDelaying = !1),
                  (e.earlyData = null),
                  (e.isEarlyCloseFlag = !1),
                  (e.earlyCloseData = null),
                  (e.waitEarlyDataRetryInterval = null),
                  (e.waitEarlyCloseDataRetryInterval = null),
                  (e.delayEarlyTween = void 0),
                  (e.isSendClose = !1),
                  (e.cheatMgEmptySpinFlag = !1),
                  (e.originGameData = null),
                  e
                );
              }
              e(n, t);
              var r = n.prototype;
              return (
                (r.init = function () {
                  (this.data = {
                    symbolPosConfig: new Map(),
                    gameState: null,
                    definition: null,
                    isResuming: !1,
                    parser: {
                      view1D: [],
                      newTimesSymbols: [],
                      winOdds: [],
                      bigwinReach: null,
                      isFullCombo: !1,
                    },
                    winBoardPosition: s(),
                    currentTimesPosition: s(),
                  }),
                    p.init(),
                    (this.data.symbolPosConfig = p.symbolPosConfig),
                    "landscape" == S.getViewModeParam()
                      ? ((this.data.winBoardPosition = s(50, 290, 0)),
                        (this.data.currentTimesPosition = s(388, 264, 0)))
                      : ((this.data.winBoardPosition = s(50, -282, 0)),
                        (this.data.currentTimesPosition = s(293, 264, 0)));
                }),
                (r.onDestory = function () {}),
                (r.clear = function () {}),
                (r.debug = function () {
                  Log.d("" + this.module);
                }),
                (r.parseView = function (t) {
                  this.data.parser.view1D = o.flattenArray(t.view);
                }),
                (r.parseTimesSymbols = function (t) {
                  var e,
                    a,
                    i = t.action,
                    n = t.currentView,
                    s = t.timesSymbols,
                    r =
                      null == (e = this.preData.gameState)
                        ? void 0
                        : e.winSymbols,
                    o =
                      null == (a = this.preData.gameState)
                        ? void 0
                        : a.timesSymbols;
                  r &&
                    o &&
                    ((this.data.parser.newTimesSymbols = []),
                    0 == n || (!r.length && "freeSpin" == i)
                      ? (this.data.parser.newTimesSymbols = s)
                      : s.length > o.length &&
                        (this.data.parser.newTimesSymbols = s.slice(o.length)));
                }),
                (r.parseNewTimesSymbols = function (t) {
                  var e,
                    a,
                    i = t.action,
                    n = t.currentView,
                    s = t.timesSymbols,
                    r = null == (e = this.preSpinData) ? void 0 : e.winSymbols,
                    o =
                      null == (a = this.preSpinData) ? void 0 : a.timesSymbols;
                  r &&
                    o &&
                    ((this.data.parser.newTimesSymbols = []),
                    0 == n || (!r.length && "freeSpin" == i)
                      ? (this.data.parser.newTimesSymbols = s)
                      : s.length > o.length &&
                        (this.data.parser.newTimesSymbols = s.slice(o.length)));
                }),
                (r.ReplayParseView = function (t) {
                  this.data.parser.view1D = o.flattenArray(t.engine.view);
                }),
                (r.ReplayParseTimesSymbols = function (t) {
                  var e,
                    a,
                    i = t.engine,
                    n = i.action,
                    s = i.currentView,
                    r = i.timesSymbols,
                    o =
                      null == (e = this.preData.gameState)
                        ? void 0
                        : e.winSymbols,
                    l =
                      null == (a = this.preData.gameState)
                        ? void 0
                        : a.timesSymbols;
                  o &&
                    l &&
                    ((this.data.parser.newTimesSymbols = []),
                    0 == s || (!o.length && "freeSpin" == n)
                      ? (this.data.parser.newTimesSymbols = r)
                      : r.length > l.length &&
                        (this.data.parser.newTimesSymbols = r.slice(l.length)));
                }),
                (r.setPreData = function () {
                  this.preData = JSON.parse(JSON.stringify(this.data));
                }),
                (r.setPreSpinData = function () {
                  this.preSpinData = JSON.parse(
                    JSON.stringify(this.currSpinData)
                  );
                }),
                (r.parseReplayWinOddsType = function (t) {
                  for (
                    var e = Object.keys(t),
                      a = Object.values(t).sort(function (t, e) {
                        return t < e ? -1 : t > e ? 1 : 0;
                      }),
                      i = 0;
                    i < e.length;
                    i++
                  )
                    this.data.parser.winOdds.push({
                      level: i,
                      reachRate: a[i],
                    });
                  Log.w("parseReplayWinOddsType", this.data.parser.winOdds);
                }),
                (r.parseWinOddsTypes = function (t) {
                  var e = t.winOddsTypes,
                    a = Object.keys(e),
                    i = Object.values(e).sort(function (t, e) {
                      return t < e ? -1 : t > e ? 1 : 0;
                    });
                  Log.w("BigWinOdd values::::::::::", i);
                  for (var n = 0; n < a.length; n++)
                    this.data.parser.winOdds.push({
                      level: n,
                      reachRate: i[n],
                    });
                  Log.w("parseWinOddsTypes", this.data.parser.winOdds);
                }),
                (r.parseFullCombo = function (t) {
                  this.data.parser.isFullCombo = t.every(function (e) {
                    return e === t[0];
                  });
                }),
                (r.setNewInitData = function (t) {
                  var e = t.engine,
                    a = t.isResuming;
                  (this.data.newGameState = e.gameState.slice()),
                    this.setPreSpinData(),
                    (this.data.definition = e.definition),
                    (this.data.isResuming = a),
                    (this.data.spinId = e.spinId),
                    0 == this.data.isResuming &&
                      (this.currSpinIndex = this.data.newGameState.length - 1),
                    (this.data.gameState = this.currSpinData),
                    this.parseView(this.currSpinData),
                    this.parseWinOddsTypes(e.definition),
                    this.parseFullCombo(this.data.parser.view1D);
                }),
                (r.setNewSpinData = function (t) {
                  var e = t.engine;
                  (this.data.newGameState = e.gameState.slice()),
                    (this.data.spinId = e.spinId),
                    (this.currSpinIndex = 0),
                    this.setPreSpinData(),
                    (this.data.gameState = this.currSpinData),
                    this.parseView(this.currSpinData),
                    this.parseNewTimesSymbols(this.currSpinData),
                    this.parseFullCombo(this.data.parser.view1D);
                }),
                (r.judgeIsOpenEarlyFlag = function () {
                  if (
                    1 == this.data.newGameState.length &&
                    (m.spinsRemaining > 1 || -1 == m.spinsRemaining) &&
                    m.active &&
                    h.isTurbo &&
                    this.currentGameType == d.MAIN_GAME
                  ) {
                    this.isOpenEarlyFlag = !0;
                    var t = this.data.newGameState[0].noWinReward;
                    t && t > 0 && (this.isOpenEarlyFlag = !1);
                  } else (this.isOpenEarlyFlag = !1), (this.earlyData = null);
                }),
                (r.setNextSpinData = function () {
                  this.setPreSpinData(),
                    this.currSpinIndex++,
                    (this.data.gameState = this.currSpinData),
                    this.parseView(this.currSpinData),
                    this.parseNewTimesSymbols(this.currSpinData),
                    this.parseFullCombo(this.data.parser.view1D);
                }),
                (r.setReplayCurrentView = function (t) {
                  this.setPreData(),
                    (this.data.gameState = t.engine),
                    this.ReplayParseView(t),
                    this.ReplayParseTimesSymbols(t);
                }),
                (r.setReplayInit = function (t) {
                  var e = t.definition
                      ? t.definition.digital
                      : y.getData().digital,
                    i = t.definition
                      ? t.definition.winOddsTypes
                      : y.getData().winOddsTypes,
                    n = t.definition
                      ? t.definition.extraFgRounds
                      : y.getData().extraFgRounds;
                  (this.data.definition = a(
                    {
                      digital: e,
                      winOddsTypes: this.parseReplayWinOddsType(i),
                      extraFgRounds: n,
                    },
                    this.data.definition
                  )),
                    (h.getData().autoCloseTime = 3),
                    (h.getData().bigwinAutoCloseTime = 5);
                }),
                (r.setBigWinReach = function (t) {
                  var e = this.data.gameState.totalStake,
                    a = this.data.parser.winOdds,
                    i = t / e;
                  this.data.parser.bigwinReach = null;
                  for (var n = 0; n < a.length; n++)
                    i >= a[n].reachRate &&
                      (this.data.parser.bigwinReach = a[n]);
                  return this.data.parser.bigwinReach;
                }),
                (r.setNewBigWinReach = function (t) {
                  var e = this.currSpinData.totalStake,
                    a = this.data.parser.winOdds,
                    i = t / e;
                  this.data.parser.bigwinReach = null;
                  for (var n = 0; n < a.length; n++)
                    i >= a[n].reachRate &&
                      (this.data.parser.bigwinReach = a[n]);
                  return this.data.parser.bigwinReach;
                }),
                (r.getSymbolSpriteFrame = function (t) {
                  var e = h.getData().filePaths.symbolsSpriteFrame,
                    a = "symbol_" + t,
                    i = App.cache.get(n.module, e).data.find(function (t) {
                      return t.name === a;
                    });
                  if (!i) throw new Error("NOT FIND 所需圖片 " + a);
                  return i;
                }),
                (r.getAtlasSymbolSpriteFrame = function (t) {
                  var e = h.getData().filePaths.symbolsAtlas,
                    a = "symbol_" + t,
                    i = w.getDirAtlas(this.module, e, a);
                  if (!i) throw new Error("NOT FIND 所需圖片 " + a);
                  return i;
                }),
                (r.getAtlasSymbolBlurSpriteFrame = function (t) {
                  var e = h.getData().filePaths.symbolsBlurAtlas,
                    a = "symbol_" + t,
                    i = w.getDirAtlas(this.module, e, a);
                  if (!i) throw new Error("NOT FIND 所需圖片 " + a);
                  return i;
                }),
                (r.getSymbolSpriteFrameBlur = function (t) {
                  var e = h.getData().filePaths.symbolsSpriteFrameBlur,
                    a = "symbol_" + t,
                    i = App.cache.get(n.module, e).data.find(function (t) {
                      return t.name === a;
                    });
                  if (!i) throw new Error("NOT FIND 所需圖片 " + a);
                  return i;
                }),
                (r.getSymbolAnimSpine = function (t) {
                  var e = h.getData().filePaths.symbolsSkeletonData,
                    a = "symbol_" + t,
                    i = App.cache.get(n.module, e).data.find(function (t) {
                      return t.name === a;
                    });
                  if (!i) throw new Error("NOT FIND 所需sp.SkeletonData " + a);
                  return i;
                }),
                (r.getGameAlertSpine = function (t) {
                  var e = h.getData().filePaths.gameAlertsSkeletonData,
                    a = App.cache.get(n.module, e).data.find(function (e) {
                      return e.name === t;
                    });
                  if (!a) throw new Error("NOT FIND 所需sp.SkeletonData " + t);
                  return a;
                }),
                (r.getCommonSpriteFrame = function (t) {
                  var e = h.getData().filePaths.common,
                    a = App.cache.get(n.module, e).data.find(function (e) {
                      return e.name === t;
                    });
                  if (!a) throw new Error("NOT FIND 所需spriteFrame " + t);
                  return a;
                }),
                (r.getLocaleSpriteFrame = function (t) {
                  var e = h.getData().filePaths.localeSpriteFrame,
                    a = App.cache.get(n.module, e).data.find(function (e) {
                      return e.name === t;
                    });
                  if (!a) throw new Error("NOT FIND 所需spriteFrame " + t);
                  return a;
                }),
                (r.getTransitionSpine = function (t) {
                  var e = h.getData().filePaths.transitionsSkeletonData,
                    a = App.cache.get(n.module, e).data.find(function (e) {
                      return e.name === t;
                    });
                  if (!a) throw new Error("NOT FIND 所需skeletonData " + t);
                  return a;
                }),
                (r.getIsFGFinish = function () {
                  var t = this.data.gameState,
                    e = t.currentView,
                    a = t.totalViews,
                    i = (t.spinId, t.startFreeGame, t.action);
                  return e + 1 === a && "freeSpin" == i;
                }),
                (r.getIsBigWinReach = function () {
                  return null != this.data.parser.bigwinReach;
                }),
                (r.saveOriginGameData = function () {
                  (this.originGameData = c.clone(this.data)),
                    g.saveOriginData(),
                    f.saveOriginData();
                }),
                (r.restoreCurrentGameData = function () {
                  this.originGameData
                    ? ((this.data = c.clone(this.originGameData)),
                      (this.currentGameType = d.MAIN_GAME),
                      (this.originGameData = null))
                    : console.warn("No originGameData to restore."),
                    g.restoreCurrentData(),
                    f.restoreCurrentData();
                }),
                i(n, [
                  {
                    key: "currentGameType",
                    get: function () {
                      return this._currentGameType;
                    },
                    set: function (t) {
                      (this.previousGameType = this._currentGameType),
                        (this._currentGameType = t),
                        dispatch(u.UPDATE_GAME_TYPE, {
                          data: this._currentGameType,
                        });
                    },
                  },
                  {
                    key: "currSpinData",
                    get: function () {
                      return this.data.newGameState[this.currSpinIndex];
                    },
                  },
                ]),
                n
              );
            })(l)
          ).module = r[r.g1001]),
          n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameEntry.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./UrlUtils.ts",
    "./Config.ts",
    "./Bundles.ts",
    "./HeartbetJson.ts",
    "./Resource.ts",
    "./Entry.ts",
    "./Decorators.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./ColorModel.ts",
    "./PlatformModel.ts",
    "./ReadyBundleModel.ts",
    "./ReplayModel.ts",
    "./UrlModel.ts",
    "./type2.ts",
    "./CmmSlotUtils.ts",
    "./SlotTableViewL.ts",
    "./SlotTableViewL_v2.ts",
    "./SlotTableViewP.ts",
    "./RegisterNewCommands.ts",
    "./BigwinView.ts",
    "./BuyFeatureView.ts",
    "./IntroView.ts",
    "./TreasuresView.ts",
    "./GameColor.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameLanguage.ts",
    "./GameHandler.ts",
    "./GameSender.ts",
    "./GameService.ts",
    "./GameView.ts",
  ],
  function () {
    "use strict";
    var e,
      t,
      n,
      a,
      r,
      o,
      i,
      s,
      u,
      l,
      c,
      d,
      p,
      f,
      g,
      b,
      m,
      h,
      y,
      w,
      v,
      A,
      S,
      L,
      k,
      C,
      x,
      D,
      M,
      E,
      P,
      B,
      _,
      I,
      F,
      V,
      G,
      R,
      T,
      O,
      U,
      N,
      H,
      z,
      W,
      Z;
    return {
      setters: [
        function (r) {
          (e = r.inheritsLoose),
            (t = r.createClass),
            (n = r.asyncToGenerator),
            (a = r.regeneratorRuntime);
        },
        function (e) {
          (r = e.cclegacy),
            (o = e.Color),
            (i = e.SpriteFrame),
            (s = e.Prefab),
            (u = e.sp),
            (l = e.Font),
            (c = e.AudioClip),
            (d = e.v3);
        },
        function (e) {
          p = e.default;
        },
        function (e) {
          (f = e.Config), (g = e.ViewZOrder);
        },
        function (e) {
          b = e.EBundles;
        },
        function (e) {
          m = e.HeartbeatJson;
        },
        function (e) {
          h = e.Resource;
        },
        function (e) {
          y = e.Entry;
        },
        function (e) {
          w = e.registerEntry;
        },
        function (e) {
          v = e.default;
        },
        function (e) {
          A = e.SlotFrameworkEvent;
        },
        function (e) {
          S = e.default;
        },
        function (e) {
          L = e.default;
        },
        function (e) {
          k = e.default;
        },
        function (e) {
          C = e.default;
        },
        function (e) {
          x = e.default;
        },
        function (e) {
          D = e.ESpinStatus;
        },
        function (e) {
          M = e.CmmSlotUtils;
        },
        function (e) {
          E = e.default;
        },
        function (e) {
          P = e.default;
        },
        function (e) {
          B = e.default;
        },
        function (e) {
          _ = e.default;
        },
        function (e) {
          I = e.BigwinView;
        },
        function (e) {
          F = e.BuyFeatureView;
        },
        function (e) {
          V = e.IntroView;
        },
        function (e) {
          G = e.TreasuresView;
        },
        function (e) {
          R = e.GameColor;
        },
        function (e) {
          (T = e.EBTM), (O = e.default);
        },
        function (e) {
          U = e.default;
        },
        function (e) {
          N = e.GameLanguage;
        },
        function (e) {
          H = e.GameHandler;
        },
        function (e) {
          z = e.GameSender;
        },
        function (e) {
          W = e.GameService;
        },
        function (e) {
          Z = e.default;
        },
      ],
      execute: function () {
        var j;
        r._RF.push({}, "24651MF5wpM+Y8jB1FsEFaR", "GameEntry", void 0);
        w(
          "GameEntry",
          b[b.g1001],
          Z
        )(
          (j = (function (r) {
            function y() {
              for (
                var e, t = arguments.length, n = new Array(t), a = 0;
                a < t;
                a++
              )
                n[a] = arguments[a];
              return (
                ((e = r.call.apply(r, [this].concat(n)) || this).language =
                  new N()),
                (e.color = new R()),
                e
              );
            }
            e(y, r);
            var w = y.prototype;
            return (
              (w.addNetHandler = function () {
                App.handlerManager.get(H);
              }),
              (w.removeNetHandler = function () {}),
              (w.loadResources = (function () {
                var e = n(
                  a().mark(function e(t) {
                    var n,
                      r,
                      o,
                      d,
                      p,
                      f,
                      g,
                      m,
                      y,
                      w,
                      v,
                      A,
                      S,
                      L,
                      C,
                      x,
                      D,
                      M,
                      E = this;
                    return a().wrap(
                      function (e) {
                        for (;;)
                          switch ((e.prev = e.next)) {
                            case 0:
                              return (
                                (n = O.getData().filePaths),
                                (r = n.symbolsSpriteFrame),
                                (o = n.symbolPrefab),
                                (d = n.symbolsSkeletonData),
                                (p = n.winCashPrefab),
                                (f = n.fireBallPrefab),
                                (g = n.gameAlertsSkeletonData),
                                (m = n.spinSkeleton),
                                (y = n.common),
                                (w = n.localeSpriteFrame),
                                (v = n.font),
                                (A = n.timesMovingPrefab),
                                (S = n.transitionsSkeletonData),
                                (L = n.buyFeatureBtnPrefab),
                                (C = n.blueTimesMovingPrefab),
                                (x = n.purpleTimesMovingPrefab),
                                (D = n.symbolsSpriteFrameBlur),
                                n.symbolsAtlas,
                                n.symbolsBlurAtlas,
                                (M = n.introSkeleton),
                                (e.next = 3),
                                this.setLoadingDataVO()
                              );
                            case 3:
                              (this.loader.getLoadResources = function () {
                                return [
                                  { preloadView: Z, bundle: E.bundle },
                                  { dir: r, bundle: E.bundle, type: i },
                                  { dir: D, bundle: E.bundle, type: i },
                                  { url: o, bundle: E.bundle, type: s },
                                  { url: p, bundle: E.bundle, type: s },
                                  { url: f, bundle: E.bundle, type: s },
                                  { url: A, bundle: E.bundle, type: s },
                                  { url: C, bundle: E.bundle, type: s },
                                  { url: x, bundle: E.bundle, type: s },
                                  { url: L, bundle: E.bundle, type: s },
                                  {
                                    dir: d,
                                    bundle: E.bundle,
                                    type: u.SkeletonData,
                                  },
                                  {
                                    dir: g,
                                    bundle: E.bundle,
                                    type: u.SkeletonData,
                                  },
                                  {
                                    dir: m,
                                    bundle: E.bundle,
                                    type: u.SkeletonData,
                                  },
                                  {
                                    dir: S,
                                    bundle: E.bundle,
                                    type: u.SkeletonData,
                                  },
                                  {
                                    dir: M,
                                    bundle: E.bundle,
                                    type: u.SkeletonData,
                                  },
                                  { dir: y, bundle: E.bundle, type: i },
                                  { dir: w, bundle: E.bundle, type: i },
                                  { dir: v, bundle: E.bundle, type: l },
                                  {
                                    url: T.WIN_LOOP,
                                    bundle: E.bundle,
                                    type: c,
                                  },
                                  {
                                    url: T.S_PRIZE_LOOP,
                                    bundle: E.bundle,
                                    type: c,
                                  },
                                  {
                                    url: T.L_PRIZE_LOOP,
                                    bundle: E.bundle,
                                    type: c,
                                  },
                                  { preloadView: F, bundle: E.bundle },
                                  { preloadView: G, bundle: E.bundle },
                                  { preloadView: I, bundle: E.bundle },
                                ];
                              }),
                                (this.loader.onLoadProgress = function (
                                  e,
                                  t,
                                  n
                                ) {
                                  App.gameLoading.setLoading(e, t, n);
                                }),
                                (this.loader.onLoadComplete = function (e) {
                                  h.LoaderError.SUCCESS &&
                                    (k.setComplete(b[E.bundle]), t());
                                }),
                                this.loader.loadResources();
                            case 7:
                            case "end":
                              return e.stop();
                          }
                      },
                      e,
                      this
                    );
                  })
                );
                return function (t) {
                  return e.apply(this, arguments);
                };
              })()),
              (w.initData = function () {
                Log.e(
                  " 🐽🐽🐽 gv" +
                    this.data.GAME_VERSION +
                    " sv" +
                    this.slotData.SLOT_VERSION +
                    " 🐽🐽🐽 "
                ),
                  _.execute(),
                  App.serviceManager.get(W, !0),
                  this.initColorModel(),
                  this.initLanguage();
              }),
              (w.initColorModel = function () {
                var e = {
                  mainGame: {
                    auxiliary: new o("#4e3487"),
                    main: new o("#ab84ff"),
                    mainHover: new o("#896acc"),
                    topbar: new o(42, 26, 77, 209.1),
                  },
                  record: {
                    5: new o(255, 255, 255, 12.75),
                    10: new o(255, 255, 255, 255 * 0.24),
                  },
                  background: {
                    0: new o("#c9c9cc"),
                    20: new o("#a9a9ad"),
                    40: new o("#88898e"),
                    60: new o("#68696f"),
                    80: new o("#474951"),
                    100: new o("#272932"),
                  },
                  white: {
                    info01: new o("#ffffff"),
                    default01: new o(255, 255, 255, 38.25),
                    default02: new o(255, 255, 255, 255 * 0.24),
                    hover01: new o(255, 255, 255, 76.5),
                    hover02: new o(255, 255, 255, 255 * 0.08),
                    labelDefault01: new o(255, 255, 255, 153),
                    textAuto01: new o("#ffffff"),
                  },
                  red: { primary: new o("#ff6433") },
                  green: { primary: new o("#3ae300") },
                  yellow: {
                    primary: new o("#ffd680"),
                    secondary: new o(255, 168, 0, 76.5),
                  },
                };
                S.setData(e);
              }),
              (w.pauseMessageQueue = function () {}),
              (w.resumeMessageQueue = function () {}),
              (w.onEnter = function (e) {
                r.prototype.onEnter.call(this, e),
                  Log.d("--------------onEnterLogin--------------"),
                  this.serviceInit();
              }),
              (w.openGameView = function (e) {
                var t = this;
                App.gameLoading.setMessage(
                  "gv" +
                    this.data.GAME_VERSION +
                    " sv" +
                    this.slotData.SLOT_VERSION
                );
                var n = setInterval(function () {
                  t.checkCompletion(n, e);
                }, 100);
              }),
              (w.onUnloadBundle = function () {
                r.prototype.onUnloadBundle.call(this);
              }),
              (w.checkCompletion = (function () {
                var e = n(
                  a().mark(function e(t, n) {
                    var r,
                      o = this;
                    return a().wrap(
                      function (e) {
                        for (;;)
                          switch ((e.prev = e.next)) {
                            case 0:
                              if (((r = App.gameLoading), k.isComplete())) {
                                e.next = 5;
                                break;
                              }
                              return e.abrupt("return");
                            case 5:
                              return (
                                clearInterval(t),
                                App.uiManager.open({
                                  type: this.gameViewType,
                                  bundle: this.bundle,
                                  args: n,
                                }),
                                (e.next = 10),
                                this.waitSocketConnected()
                              );
                            case 10:
                              if (!p.hasParam("spinId")) {
                                e.next = 18;
                                break;
                              }
                              (C.isReplay = !0),
                                Log.d("hasReplayUrl", C.isReplay),
                                App.senderManager.get(z).replay(),
                                r.complete(),
                                (e.next = 20);
                              break;
                            case 18:
                              return (
                                (e.next = 20),
                                App.senderManager
                                  .get(z)
                                  .initial()
                                  .then(function () {
                                    r.hideProgressBar(),
                                      r.hideGameLogo(),
                                      App.uiManager.open({
                                        type: V,
                                        bundle: o.bundle,
                                        zIndex: g.UILoading,
                                        name: "Intro",
                                      });
                                    var e = L.getData().slotTablesOn,
                                      t = o.data.getData().isResuming,
                                      n =
                                        "1" === x.getData().searchParams.table;
                                    if (e && !t) {
                                      if (n) return;
                                      var a =
                                          "egyptian-mythology" ===
                                          p.getParam("gn")
                                            ? P
                                            : E,
                                        i = M.getOrientationTarget(a, B);
                                      App.uiManager.open({
                                        type: i,
                                        bundle: b[b.slotFramework],
                                        zIndex: g.UI,
                                        name: "機台選擇",
                                        args: !0,
                                      });
                                    }
                                    dispatch(A.UPDATE_SPIN_STATUS, {
                                      data: D.IDLE,
                                    });
                                  })
                              );
                            case 20:
                            case "end":
                              return e.stop();
                          }
                      },
                      e,
                      this
                    );
                  })
                );
                return function (t, n) {
                  return e.apply(this, arguments);
                };
              })()),
              (w.setLoadingDataVO = (function () {
                var e = n(
                  a().mark(function e() {
                    var t, n, r, o, s, l, c, f, g, b, m, h, y, w;
                    return a().wrap(
                      function (e) {
                        for (;;)
                          switch ((e.prev = e.next)) {
                            case 0:
                              return (
                                (t = p.getViewModeParam()),
                                (r = x.getData().searchParams.l),
                                (e.next = 4),
                                App.cache.getCacheByAsync(
                                  "assets/texture/common/" +
                                    t +
                                    "/l_bg/spriteFrame",
                                  i,
                                  this.bundle
                                )
                              );
                            case 4:
                              return (
                                (o = e.sent),
                                (e.next = 7),
                                App.cache.getCacheByAsync(
                                  "assets/texture/locale/" +
                                    t +
                                    "/" +
                                    r +
                                    "/l_font/spriteFrame",
                                  i,
                                  this.bundle
                                )
                              );
                            case 7:
                              return (
                                (s = e.sent),
                                (e.next = 10),
                                App.cache.getCacheByAsync(
                                  "assets/texture/locale/" +
                                    t +
                                    "/" +
                                    r +
                                    "/l_logo/spriteFrame",
                                  i,
                                  this.bundle
                                )
                              );
                            case 10:
                              return (
                                (l = e.sent),
                                (e.next = 13),
                                App.cache.getCacheByAsync(
                                  "assets/texture/common/" +
                                    t +
                                    "/l_loading_01/spriteFrame",
                                  i,
                                  this.bundle
                                )
                              );
                            case 13:
                              return (
                                (c = e.sent),
                                (e.next = 16),
                                App.cache.getCacheByAsync(
                                  "assets/texture/common/" +
                                    t +
                                    "/l_loading_02/spriteFrame",
                                  i,
                                  this.bundle
                                )
                              );
                            case 16:
                              return (
                                (f = e.sent),
                                (e.next = 19),
                                App.cache.getCacheByAsync(
                                  "assets/texture/common/" +
                                    t +
                                    "/l_loading_frame/spriteFrame",
                                  i,
                                  this.bundle
                                )
                              );
                            case 19:
                              return (
                                (g = e.sent),
                                (e.next = 22),
                                App.cache.getCacheByAsync(
                                  "assets/texture/common/" +
                                    t +
                                    "/l_loading_light/spriteFrame",
                                  i,
                                  this.bundle
                                )
                              );
                            case 22:
                              if (
                                ((b = e.sent), (m = null), "landscape" != t)
                              ) {
                                e.next = 33;
                                break;
                              }
                              return (
                                (e.next = 27),
                                App.cache.getCacheByAsync(
                                  "assets/spine/" + t + "/loading/loading",
                                  u.SkeletonData,
                                  this.bundle
                                )
                              );
                            case 27:
                              (h = e.sent),
                                (n = {
                                  background: o,
                                  spine: h,
                                  barFrame: g,
                                  bar: c,
                                  barbg: f,
                                  barLight: b,
                                  logo: l,
                                  startGame: s,
                                }),
                                (y = {
                                  left: 20,
                                  isAlignLeft: !0,
                                  isAlignTop: !0,
                                  top: 10,
                                }),
                                App.gameLoading.setLogoWidget(y),
                                (e.next = 34);
                              break;
                            case 33:
                              "portrait" == t &&
                                ((n = {
                                  background: o,
                                  barFrame: g,
                                  bar: c,
                                  barbg: f,
                                  barLight: b,
                                  logo: l,
                                  startGame: s,
                                }),
                                (w = {
                                  bottom: 135,
                                  isAlignBottom: !0,
                                  isAlignHorizontalCenter: !0,
                                  horizontalCenter: 0,
                                }),
                                App.gameLoading.setLogoWidget(w),
                                (m = { mask: d(0, 0, 0) }));
                            case 34:
                              App.gameLoading.setData(n, m);
                            case 35:
                            case "end":
                              return e.stop();
                          }
                      },
                      e,
                      this
                    );
                  })
                );
                return function () {
                  return e.apply(this, arguments);
                };
              })()),
              (w.serviceInit = function () {
                (this.service.heartbeat = m),
                  (this.service.maxEnterBackgroundTime =
                    f.MIN_INBACKGROUND_TIME),
                  this.service.connect(),
                  (this.service.enabled = !0);
              }),
              (w.initLanguage = function () {
                var e,
                  t =
                    null != (e = x.getData().searchParams) && e.l
                      ? x.getData().searchParams.l
                      : "zh-tw";
                App.language.change(t);
              }),
              (w.waitSocketConnected = (function () {
                var e = n(
                  a().mark(function e() {
                    var t = this;
                    return a().wrap(function (e) {
                      for (;;)
                        switch ((e.prev = e.next)) {
                          case 0:
                            return e.abrupt(
                              "return",
                              new Promise(function (e, n) {
                                var a = 0,
                                  r = setInterval(function () {
                                    t.service.isConnected
                                      ? (clearInterval(r), e())
                                      : (a += 100) >= 3e4 &&
                                        (clearInterval(r),
                                        n(
                                          new Error(
                                            "Socket connection timed out"
                                          )
                                        ));
                                  }, 100);
                              })
                            );
                          case 1:
                          case "end":
                            return e.stop();
                        }
                    }, e);
                  })
                );
                return function () {
                  return e.apply(this, arguments);
                };
              })()),
              t(y, [
                {
                  key: "service",
                  get: function () {
                    return App.serviceManager.get(W);
                  },
                },
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(U);
                  },
                },
                {
                  key: "slotData",
                  get: function () {
                    return App.dataCenter.get(v);
                  },
                },
              ]),
              y
            );
          })(y))
        );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameEvent.ts",
  ["./rollupPluginModLoBabelHelpers.js", "cc", "./FlowEvent.ts"],
  function (_) {
    "use strict";
    var E, A, S;
    return {
      setters: [
        function (_) {
          E = _.inheritsLoose;
        },
        function (_) {
          A = _.cclegacy;
        },
        function (_) {
          S = _.FlowEvent;
        },
      ],
      execute: function () {
        A._RF.push({}, "396b38eNY9JtKK37nxATabD", "GameEvent", void 0);
        var T = _(
          "GameEvent",
          (function (_) {
            function A() {
              return _.apply(this, arguments) || this;
            }
            return E(A, _), A;
          })(S)
        );
        (T.CREATE_SPIN_FLOW = "GameEvent:CREATE_SPIN_FLOW"),
          (T.CREATE_STOP_SPIN_FLOW = "GameEvent:CREATE_STOP_SPIN_FLOW"),
          (T.CREATE_SPIN_COMPLETE_FLOW = "GameEvent:CREATE_SPIN_COMPLETE_FLOW"),
          (T.CREATE_CLOSE_SPIN_FLOW = "GameEvent:CREATE_CLOSE_SPIN_FLOW"),
          (T.SPIN_CLOSED_FLOW = "GameEvent:SPIN_CLOSED_FLOW"),
          (T.CREATE_RESUME_FLOW = "GameEvent:CREATE_RESUME_FLOW"),
          (T.CREATE_QUICK_STOP_FLOW = "GameEvent:CREATE_QUICK_STOP_FLOW"),
          (T.CREATE_EARLY_SPIN_FLOW = "GameEvent:CREATE_EARLY_SPIN_FLOW"),
          (T.WAIT_EARLY_SPIN_RESPONSE = "GameEvent:WAIT_EARLY_SPIN_RESPONSE"),
          (T.SET_EARLY_SPIN_DATA_TO_SPIN =
            "GameEvent:SET_EARLY_SPIN_DATA_TO_SPIN"),
          (T.EARLY_SPIN_DELAYING = "SlotFramework:EARLY_SPIN_DELAYING"),
          (T.SET_EARLY_SPIN_DELAYING_COMPLETED =
            "SlotFramework:SET_EARLY_SPIN_DELAYING_COMPLETED"),
          (T.SPIN_START = "GameEvent:START_SPIN"),
          (T.SPIN_CLOSED = "GameEvent:SPIN_CLOSED"),
          (T.AUTO_SPIN_STATUS = "GameEvent:AUTO_SPIN_STATUS"),
          (T.UPDATE_GAME_TYPE = "GameEvent:UPDATE_GAME_TYPE"),
          (T.SHOW_SYMBOLS_OUT_ANIM = "GameEvent:SHOW_SYMBOLS_OUT_ANIM"),
          (T.SHOW_SYMBOLS_IN_ANIM = "GameEvent:SHOW_SYMBOLS_IN_ANIM"),
          (T.SHOW_SYMBOLS_QUICK_IN_ANIM =
            "GameEvent:SHOW_SYMBOLS_QUICK_IN_ANIM"),
          (T.SHOW_NEW_SYMBOLS_IN_ANIM = "GameEvent:SHOW_NEW_SYMBOLS_IN_ANIM"),
          (T.SHOW_OPEN_TIMES_SYMBOL = "GameEvent:SHOW_OPEN_TIMES_SYMBOL"),
          (T.SHOW_CHARACTER_FIRE = "GameEvent:SHOW_CHARACTER_FIRE"),
          (T.SPEED_CHARACTER_FIRE_UP = "GameEvent:SPEED_CHARACTER_FIRE_UP"),
          (T.SHOW_FIRE_BALL = "GameEvent:SHOW_FIRE_BALL"),
          (T.SHOW_FIRE_BALL_QUICK_STOP = "GameEvent:SHOW_FIRE_BALL_QUICK_STOP"),
          (T.REMOVE_FIRE_BALLS = "GameEvent:REMOVE_FIRE_BALLS"),
          (T.SHOW_TIMES_SYMBOLS_UPGRADE =
            "GameEvent:SHOW_TIMES_SYMBOLS_UPGRADE"),
          (T.SHOW_SCATTER_WIN = "GameEvent:SHOW_SCATTER_WIN"),
          (T.SHOW_FG_INTRO_ALERT = "GameEvent:SHOW_FG_INTRO_ALERT"),
          (T.SHOW_FG_SUMMARY_ALERT = "GameEvent:SHOW_FG_SUMMARY_ALERT"),
          (T.SHOW_SYMBOLS_WIN = "GameEvent:SHOW_SYMBOLS_WIN"),
          (T.REMOVE_SYMBOLS = "GameEvent:REMOVE_SYMBOLS"),
          (T.PLAY_CURRENT_VIEW_FALL_ANIM =
            "GameEvent:PLAY_CURRENT_VIEW_FALL_ANIM"),
          (T.SHOW_TIMES_MOVING = "GameEvent:SHOW_TIMES_MOVING"),
          (T.HIDE_TIMES_LABEL = "GameEvent:HIDE_TIMES_LABEL"),
          (T.EXPAND_WIN_AMOUNT = "GameEvent:EXPAND_WIN_AMOUNT"),
          (T.UPDATE_TIMES = "GameEvent:UPDATE_TIMES"),
          (T.MERGE_WIN_AMOUNT = "GameEvent:MERGE_WIN_AMOUNT"),
          (T.UPDATE_FG_TOTAL_TIMES = "GameEvent:UPDATE_FG_TOTAL_TIMES"),
          (T.PLAY_TIMES_SYMBOL_FUNCTION =
            "GameEvent:PLAY_TIMES_SYMBOL_FUNCTION"),
          (T.SHOW_WIN_CASH = "GameEvent:SHOW_WIN_CASH"),
          (T.UPDATE_WIN_AMOUNT = "GameEvent:UPDATE_WIN_AMOUNT"),
          (T.QUICK_STOP_WIN_AMOUNT = "GameEvent:QUICK_STOP_WIN_AMOUNT"),
          (T.QUICK_STOP_TOTAL_WINNINGS = "GameEvent:QUICK_STOP_TOTAL_WINNINGS"),
          (T.REPLAY_START_QUICK_STOP = "GameEvent:REPLAY_START_QUICK_STOP"),
          (T.UPDATE_FG_REMAINING = "GameEvent:UPDATE_FG_REMAINING"),
          (T.INCREASE_FG_REMAINING = "GameEvent:INCREASE_FG_REMAINING"),
          (T.SHAKE_NODE = "GameEvent:SHAKE_NODE"),
          (T.PLAY_BGM = "GameEvent:PLAY_BGM"),
          (T.PLAY_BTM = "GameEvent:PLAY_BTM"),
          (T.STOP_BTM = "GameEvent:STOP_BTM"),
          (T.MUSIC_VOLUME_MULTIPLE = "GameEvent:MUSIC_VOLUME_MULTIPLE"),
          (T.CHANGE_GAME_STYLE = "GameEvent:CHANGE_GAME_STYLE"),
          (T.SET_SYMBOL_VIEW_MASK = "GameEvent:SET_SYMBOL_VIEW_MASK"),
          (T.SHOW_JP_WIN = "GameEvent:SHOW_JP_WIN"),
          (T.SHOW_JP = "GameEvent:SHOW_JP"),
          (T.SHOW_BIGWIN = "GameEvent:SHOW_BIGWIN"),
          (T.SHOW_FULL_COMBO = "GameEvent:SHOW_FULL_COMBO"),
          (T.SHOW_TRANSITION_IN = "GameEvent:SHOW_TRANSITION_IN"),
          (T.SHOW_TRANSITION_OUT = "GameEvent:SHOW_TRANSITION_OUT"),
          (T.START_QUICK_STOP = "GameEvent:START_QUICK_STOP"),
          (T.OPEN_FEATURE_POPUP = "GameEvent:OPEN_FEATURE_POPUP"),
          (T.CLOSE_FEATURE_POPUP = "GameEvent:CLOSE_FEATURE_POPUP"),
          (T.SHOW_TREASURE_VIEW = "GameEvent:SHOW_TREASURE_VIEW"),
          (T.PARSER_INIT_COMPLETED = "GameEvent:PARSER_INIT_COMPLETED"),
          (T.PARSER_SPIN_COMPLETED = "GameEvent:PARSER_SPIN_COMPLETED"),
          (T.PARSER_CLOSE_SPIN_COMPLETED =
            "GameEvent:PARSER_CLOSE_SPIN_COMPLETED"),
          (T.EARLY_DATA_PARSER_TO_SPIN_DATA =
            "GameEvent:EARLY_DATA_PARSER_TO_SPIN_DATA"),
          (T.EARLY_CLOSE_DATA_PARSER_TO_DATA =
            "GameEvent:EARLY_CLOSE_DATA_PARSER_TO_DATA"),
          (T.WAIT_EARLY_DATA_RETRY = "GameEvent:WAIT_EARLY_DATA_RETRY"),
          (T.WAIT_EARLY_CLOSE_DATA_RETRY =
            "GameEvent:WAIT_EARLY_CLOSE_DATA_RETRY"),
          (T.KILL_WAIT_EARLY_DATA_RETRY_INTERVAL =
            "GameEvent:KILL_WAIT_EARLY_DATA_RETRY_INTERVAL"),
          (T.KILL_WAIT_EARLY_CLOSE_DATA_RETRY_INTERVAL =
            "GameEvent:KILL_WAIT_EARLY_CLOSE_DATA_RETRY_INTERVAL"),
          (T.CREATE_REPLAY_FLOW = "GameEvent:CREATE_REPLAY_FLOW"),
          (T.CREATE_REPLAY_SPIN_FLOW = "GameEvent:CREATE_REPLAY_SPIN_FLOW"),
          (T.CREATE_REPLAY_STOP_SPIN_FLOW =
            "GameEvent:CREATE_REPLAY_STOP_SPIN_FLOW"),
          (T.CREATE_REPLAY_SPIN_COMPLETE_FLOW =
            "GameEvent:CREATE_REPLAY_SPIN_COMPLETE_FLOW"),
          (T.CREATE_REPLAY_CLOSE_SPIN_FLOW =
            "GameEvent:CREATE_REPLAY_CLOSE_SPIN_FLOW"),
          (T.PARSER_REPLAY_COMPLETED = "GameEvent:PARSER_REPLAY_COMPLETED"),
          (T.CREATE_REPLAY_QUICK_STOP_FLOW =
            "GameEvent:CREATE_REPLAY_QUICK_STOP_FLOW"),
          (T.PROCESS_REPLAY_IN_GAME = "GameEvent:PROCESS_REPLAY_IN_GAME"),
          (T.RESET_AND_OPEN_GAME_VIEW = "GameEvent:RESET_AND_OPEN_GAME_VIEW"),
          (T.FG_START_COUNT_FOR_PLAY_LOG =
            "GameEvent:FG_START_COUNT_FOR_PLAY_LOG"),
          (T.FG_STOP_COUNT_FOR_PLAY_LOG =
            "GameEvent:FG_STOP_COUNT_FOR_PLAY_LOG"),
          (T.FG_UPDATE_SETTING_FOR_PLAY_LOG =
            "GameEvent:FG_UPDATE_SETTING_FOR_PLAY_LOG"),
          A._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameHandler.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkEvent.ts",
    "./GameHandlerBase.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./GameSender.ts",
    "./GameService.ts",
    "./PlatformModel.ts",
  ],
  function (e) {
    "use strict";
    var t, n, a, s, r, o, E, i, _, d, S, l, c, u;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (n = e.createClass);
        },
        function (e) {
          (a = e.cclegacy), (s = e.tween);
        },
        function (e) {
          r = e.EBundles;
        },
        function (e) {
          o = e.default;
        },
        function (e) {
          E = e.SlotFrameworkEvent;
        },
        function (e) {
          i = e.GameHandlerBase;
        },
        function (e) {
          (_ = e.EInitName), (d = e.default);
        },
        function (e) {
          S = e.GameEvent;
        },
        function (e) {
          l = e.GameSender;
        },
        function (e) {
          c = e.GameService;
        },
        function (e) {
          u = e.default;
        },
      ],
      execute: function () {
        a._RF.push({}, "c6ce3gApbBC8a0dysd0GX0F", "GameHandler", void 0),
          (e(
            "GameHandler",
            (function (e) {
              function a() {
                return e.apply(this, arguments) || this;
              }
              return (
                t(a, e),
                (a.prototype.addListeners = function () {
                  var e = this;
                  this.on(E.SEND_SPIN_REQUEST, function (e) {
                    var t = null == e ? void 0 : e.data,
                      n = t.spinId,
                      a = t.stakeVO,
                      s = t.cheat,
                      r = t.updateStake;
                    App.senderManager.get(l).spin(a, n, s, r);
                  }),
                    this.on(E.SEND_EARLY_SPIN_REQUEST, function (t) {
                      var n = null == t ? void 0 : t.data,
                        a = n.spinId,
                        r = n.stakeVO,
                        E = n.forceClose;
                      o.active &&
                        e.data.isOpenEarlyFlag &&
                        (Log.w("SEND_OUT_EARLY_SPIN_REQUEST::::::::"),
                        (e.data.earlyData = null),
                        (e.data.delayEarlyTween = s(e)
                          .delay(0.4)
                          .call(function () {
                            (e.data.isSendOutEarlyFlag = !0),
                              (e.data.isSendClose = !0),
                              App.senderManager.get(l).earlySpin(r, a, !1, E);
                          })
                          .start()));
                    }),
                    this.on(E.SEND_CLOSE_REQUEST, function (t) {
                      var n = t.data;
                      (e.data.isSendClose = !0),
                        1 != u.getData().isInstantClose
                          ? App.senderManager.get(l).closeSpin(n)
                          : dispatch(E.CLOSE_RESPONSE);
                    }),
                    this.on(E.SEND_EARLY_CLOSE_REQUEST, function (e) {
                      var t = e.data.spinId;
                      App.senderManager.get(l).earlyCloseSpin(t, e.complete);
                    }),
                    this.on(E.SEND_UPDATE_AVATAR_REQUEST, function (e) {
                      var t = e.avatarId;
                      App.senderManager.get(l).updateAvatar(t);
                    }),
                    this.on(
                      E.SEND_GET_SLOT_TABLE_PAGE_DATA_REQUEST,
                      function (e) {
                        App.senderManager.get(l).getSlotTablePage(e);
                      }
                    ),
                    this.on(E.SEND_GET_SLOT_TABLE_DETAIL_REQUEST, function (e) {
                      var t = e.roomId;
                      App.senderManager
                        .get(l)
                        .getSlotTableDetail({ roomId: t });
                    }),
                    this.on(E.SEND_CHANGE_SLOT_TABLE_REQUEST, function (e) {
                      App.senderManager.get(l).changeSlotTable(e);
                    }),
                    this.on(E.SEND_LOCK_SLOT_TABLE_REQUEST, function (e) {
                      App.senderManager.get(l).lockSlotTable(e);
                    }),
                    this.on(E.SEND_SETTING_REQUEST, function (e) {
                      App.senderManager.get(l).setting(e);
                    }),
                    this.on(E.SEND_GET_BET_RECORDS_REQUEST, function (e) {
                      App.senderManager.get(l).getBetRecords(e);
                    }),
                    this.on(E.SEND_UPDATE_DISPLAYNAME_REQUEST, function (e) {
                      App.senderManager.get(l).updateDisplayName(e);
                    }),
                    this.on(E.SEND_GET_HISTORY_REQUEST, function (e) {
                      App.senderManager.get(l).getHistoryRecords(e);
                    }),
                    this.on(S.FG_UPDATE_SETTING_FOR_PLAY_LOG, function (e) {
                      App.senderManager.get(l).setting(e);
                    }),
                    this.on(E.SEND_GET_RANKING_LIST_REQUEST, function (e) {
                      App.senderManager.get(l).getSlotBetRanksList(e);
                    }),
                    this.on(E.SEND_GET_RANKING_REPLAY_REQUEST, function (e) {
                      App.senderManager.get(l).getSlotBetRanksReplay(e);
                    }),
                    this.on(E.REPLAY_BACK_TO_GAME, function () {
                      e.data.restoreCurrentGameData(),
                        dispatch(S.RESET_AND_OPEN_GAME_VIEW, {
                          data: _.INIT_GAME,
                        });
                    });
                }),
                n(a, [
                  {
                    key: "data",
                    get: function () {
                      return App.dataCenter.get(d);
                    },
                  },
                  {
                    key: "service",
                    get: function () {
                      return App.serviceManager.get(c);
                    },
                  },
                ]),
                a
              );
            })(i)
          ).module = r[r.g1001]),
          a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameLanguage.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./LanguageDelegate.ts",
    "./GameData.ts",
    "./GameLanguages.ts",
  ],
  function (e) {
    "use strict";
    var n, t, a, u, i, o;
    return {
      setters: [
        function (e) {
          n = e.inheritsLoose;
        },
        function (e) {
          t = e.cclegacy;
        },
        function (e) {
          (a = e.injectLanguageData), (u = e.LanguageDelegate);
        },
        function (e) {
          i = e.default;
        },
        function (e) {
          o = e;
        },
      ],
      execute: function () {
        var c;
        t._RF.push({}, "955dfWUN0NAV5POGCeEknO0", "GameLanguage", void 0);
        e(
          "GameLanguage",
          a(
            (c = (function (e) {
              function t() {
                for (
                  var n, t = arguments.length, a = new Array(t), u = 0;
                  u < t;
                  u++
                )
                  a[u] = arguments[u];
                return (
                  ((n = e.call.apply(e, [this].concat(a)) || this).bundle =
                    i.module),
                  n
                );
              }
              return (
                n(t, e),
                (t.prototype.init = function () {
                  this.importLanguages(o);
                }),
                t
              );
            })(u))
          ) || c
        );
        t._RF.pop();
      },
    };
  }
);

System.register("chunks:///_virtual/GameLanguages.ts", ["cc"], function (a) {
  "use strict";
  var e;
  return {
    setters: [
      function (a) {
        e = a.cclegacy;
      },
    ],
    execute: function () {
      e._RF.push({}, "8f352aePrxEpIjL1lry6sSW", "GameLanguages", void 0);
      a("ZH_TW", {
        language: "zh-tw",
        data: { confirm: "確定", cancel: "取消" },
      }),
        a("ZH_CN", {
          language: "zh-cn",
          data: { confirm: "确定", cancel: "取消" },
        }),
        a("EN", {
          language: "en",
          data: { confirm: "Sure", cancel: "Cancel" },
        }),
        a("VN", { language: "vn", data: { confirm: "", cancel: "" } });
      e._RF.pop();
    },
  };
});

System.register(
  "chunks:///_virtual/GameLogic.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Config.ts",
    "./Bundles.ts",
    "./ExitUtils.ts",
    "./Resource.ts",
    "./ResourceLoader.ts",
    "./Logic.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./PlatformModel.ts",
    "./ReadyBundleModel.ts",
    "./ParseResponse.ts",
    "./BigwinView.ts",
    "./FreeGameAlertView.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./GameSender.ts",
    "./types.ts",
    "./GameView.ts",
    "./DefinitionModel.ts",
    "./BuyFeatureView.ts",
    "./FlowIDs.ts",
    "./GameConfigModel.ts",
    "./ReplayModel.ts",
    "./TreasuresView.ts",
    "./type2.ts",
  ],
  function (t) {
    "use strict";
    var e,
      a,
      n,
      i,
      r,
      o,
      l,
      s,
      u,
      c,
      p,
      d,
      E,
      A,
      _,
      f,
      S,
      I,
      g,
      y,
      T,
      R,
      h,
      L,
      m,
      P,
      v,
      w,
      O,
      D,
      C,
      N,
      b,
      F,
      M;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose),
            (a = t.asyncToGenerator),
            (n = t.regeneratorRuntime),
            (i = t.createClass);
        },
        function (t) {
          (r = t.cclegacy), (o = t.Tween), (l = t.game), (s = t.tween);
        },
        function (t) {
          u = t.ViewZOrder;
        },
        function (t) {
          c = t.EBundles;
        },
        function (t) {
          p = t.ExitUtils;
        },
        function (t) {
          d = t.Resource;
        },
        function (t) {
          E = t.default;
        },
        function (t) {
          A = t.Logic;
        },
        function (t) {
          _ = t.default;
        },
        function (t) {
          f = t.default;
        },
        function (t) {
          S = t.SlotFrameworkEvent;
        },
        function (t) {
          I = t.default;
        },
        function (t) {
          g = t.default;
        },
        function (t) {
          y = t.default;
        },
        function (t) {
          T = t.BigwinView;
        },
        function (t) {
          R = t.FreeGameAlertView;
        },
        function (t) {
          (h = t.EInitName), (L = t.default);
        },
        function (t) {
          m = t.GameEvent;
        },
        function (t) {
          P = t.GameSender;
        },
        function (t) {
          v = t.EGameType;
        },
        function (t) {
          w = t.default;
        },
        function (t) {
          O = t.default;
        },
        function (t) {
          D = t.BuyFeatureView;
        },
        function (t) {
          C = t.FlowIDs;
        },
        function (t) {
          N = t.default;
        },
        function (t) {
          b = t.default;
        },
        function (t) {
          F = t.TreasuresView;
        },
        function (t) {
          M = t.ESpinStatus;
        },
      ],
      execute: function () {
        r._RF.push({}, "027089BVJJH+5Y/iJBPx/JG", "GameLogic", void 0);
        t(
          "GameLogic",
          (function (t) {
            function r() {
              for (
                var e, a = arguments.length, n = new Array(a), i = 0;
                i < a;
                i++
              )
                n[i] = arguments[i];
              return (
                ((e = t.call.apply(t, [this].concat(n)) || this).loader =
                  new E()),
                (e.earlySpinDelayingEvent = null),
                (e.earlySpinDelayingSetTimeout = null),
                (e.earlyIntervalId = 1),
                (e.fgPlayLogIntervalId = -1),
                e
              );
            }
            e(r, t);
            var A = r.prototype;
            return (
              (A.onLoad = function (e) {
                t.prototype.onLoad.call(this, e), this._init();
              }),
              (A.onDestroy = function () {
                this.loader.unLoadResources(),
                  this.data.clear(),
                  t.prototype.onDestroy.call(this);
              }),
              (A.start = function () {
                App.senderManager.get(P).init();
              }),
              (A.reset = function () {
                o.stopAll(),
                  App.flowManager.killAllFlow(),
                  App.uiManager.closeExcept([]),
                  dispatch(S.UPDATE_SPIN_STATUS, { data: M.IDLE }),
                  this.removeAllEvents();
              }),
              (A._init = function () {
                this.loadResources();
              }),
              (A.loadResources = function () {
                (this.loader.getLoadResources = function () {
                  return [];
                }),
                  (this.loader.onLoadComplete = function (t) {
                    d.LoaderError.SUCCESS;
                  }),
                  this.loader.loadResources();
              }),
              (A.setGameType = function (t) {
                var e;
                this.data.currentGameType =
                  "spin" ===
                  (null == (e = t.engine.gameState) ? void 0 : e.action)
                    ? v.MAIN_GAME
                    : v.FREE_GAME;
              }),
              (A.addEvents = function () {
                var t = this;
                this.on(S.INIT_RESPONSE, function (t) {
                  t.engine.gameState.length
                    ? y.parseNewInit(t)
                    : y.parseInit(t);
                }),
                  this.on(S.SPIN_RESPONSE, function (t) {
                    dispatch(S.UPDATE_USER_SPIN_ID, {
                      data: { spinId: t.engine.spinId },
                    });
                    var e = I.amount;
                    I.getData().theme &&
                      "xin-star" == I.getData().theme &&
                      (e = I.betAmount),
                      dispatch(S.UPDATE_USER_BALANCE, { data: { balance: e } }),
                      y.parseNewSpin(t);
                  }),
                  this.on(S.EARLY_SPIN_RESPONSE, function (t) {
                    y.parseEarlySpin(t);
                  }),
                  this.on(S.EARLY_CLOSE_RESPONSE, function (t) {
                    y.tempEarlyClose(t);
                  }),
                  this.on(S.CLOSE_RESPONSE, function (t) {
                    y.parseCloseSpin(t);
                  }),
                  this.on(S.REPLAY_RESPONSE, function (t) {
                    y.parseReplay(t);
                  }),
                  this.on(S.REPLAY_AGAIN, function (t) {
                    y.parseReplayAgain(t);
                  }),
                  this.on(S.WRAPPER_SERVICE_CLOSE, function (t) {
                    if ("xin-star" == I.getData().theme) {
                      var e = {
                          text: App.getLanguage(
                            "disconnectXinStar",
                            [],
                            c[c.wrapper]
                          ),
                          confirmCb: function (t) {
                            a();
                          },
                          bbrCb: function (t) {},
                          needCloseAlert: !1,
                          tag: u.TopErrorAlert,
                          titleisHidden: !0,
                          expandisHidden: !0,
                          confirmisHidden: !0,
                        },
                        a = function () {
                          p.exit();
                        };
                      App.gameAlert.show(e, u.TopErrorAlert);
                    } else {
                      var n = {
                          text: App.getLanguage("disconnect", [], c[c.wrapper]),
                          confirmCb: function (t) {
                            i();
                          },
                          bbrCb: function (t) {},
                          needCloseAlert: !1,
                          tag: u.TopErrorAlert,
                          isDisableBlockInput: b.isReplay && l.isPaused(),
                        },
                        i = function () {
                          p.exit();
                        };
                      App.gameAlert.show(n, u.TopErrorAlert);
                    }
                  }),
                  this.on(S.WARN_RESPONSE, function (t) {
                    if ("xin-star" == I.getData().theme) {
                      var e = {
                          text: App.getLanguage(
                            "disconnectXinStar",
                            [],
                            c[c.wrapper]
                          ),
                          confirmCb: function (t) {
                            a();
                          },
                          bbrCb: function (t) {},
                          needCloseAlert: !1,
                          tag: u.TopErrorAlert,
                          titleisHidden: !0,
                          expandisHidden: !0,
                          confirmisHidden: !0,
                        },
                        a = function () {
                          p.exit();
                        };
                      App.gameAlert.show(e, u.TopErrorAlert);
                    } else {
                      var n = {
                          text: t.message,
                          confirmCb: function (t) {
                            i();
                          },
                          bbrCb: function (t) {},
                          needCloseAlert: !1,
                          tag: u.TopErrorAlert,
                        },
                        i = function () {
                          p.exit();
                        };
                      App.gameAlert.show(n, u.TopErrorAlert);
                    }
                    dispatch(m.FG_STOP_COUNT_FOR_PLAY_LOG);
                  }),
                  this.on(S.CLICK_GAME_LOADING_CONFIRM_BTN, function () {
                    t.view.init();
                  }),
                  this.on(m.PARSER_SPIN_COMPLETED, function () {
                    dispatch(m.CREATE_STOP_SPIN_FLOW);
                  }),
                  this.on(m.START_QUICK_STOP, function () {
                    o.stopAllByTarget(t);
                  }),
                  this.on(m.PARSER_CLOSE_SPIN_COMPLETED, function () {
                    t.data.getIsFGFinish() || dispatch(m.SPIN_CLOSED_FLOW);
                  }),
                  this.on(m.QUICK_STOP_TOTAL_WINNINGS, function (t) {
                    dispatch(S.QUICK_STOP_TOTAL_WINNINGS, { data: t.data });
                  }),
                  this.on(m.SPIN_START, function () {}),
                  this.on(m.SPIN_CLOSED, function () {}),
                  this.on(S.SELECT_AUTO_SPIN_COUNT, function (t) {
                    var e = t.data,
                      a = I.getData().player.settings.autoPlay.numberOfPlays[e];
                    (_.active = !0),
                      (_.spinsRemaining = a),
                      _.active &&
                        dispatch(m.CREATE_SPIN_FLOW, {
                          data: { spinId: null, cheat: null },
                        });
                  }),
                  this.on(S.STOP_AUTO_SPIN, function () {
                    if (
                      ((_.active = !1),
                      (_.spinsRemaining = 0),
                      App.flowManager.killOneFlow(C.EARLY_SPIN_FLOW),
                      (t.data.isEarlyCloseFlag = !1),
                      (t.data.isEarlyFlag = !1),
                      t.data.isSendOutEarlyFlag)
                    )
                      null == t.data.earlyData
                        ? Log.w("已送出預跑但還未收到資料")
                        : (Log.w("已送出預跑且收到資料"),
                          clearInterval(t.earlyIntervalId),
                          t.earlyIntervalId > -1 &&
                            ((t.earlyIntervalId = -1),
                            dispatch(m.CREATE_SPIN_FLOW, {
                              data: {
                                spinId: null,
                                cheat: null,
                                earlySpin: !0,
                              },
                            })));
                    else {
                      Log.w("尚未送出可直接取消預跑"),
                        t.data.delayEarlyTween &&
                          (t.data.delayEarlyTween.stop(),
                          t.data.delayEarlyTween.removeSelf());
                      var e = !1;
                      t.earlyIntervalId > -1 &&
                        ((e = !0),
                        clearInterval(t.earlyIntervalId),
                        (t.earlyIntervalId = -1)),
                        t.data.isOpenEarlyFlag &&
                          ((t.data.isOpenEarlyFlag = !1),
                          t.data.isSendClose ||
                            (Log.w("還未結算:::::::::::"),
                            e &&
                              dispatch(S.SEND_CLOSE_REQUEST, {
                                data: t.data.getData().spinId,
                              })));
                    }
                  }),
                  this.on(m.EARLY_SPIN_DELAYING, function (e) {
                    t.earlySpinDelayingEvent = e;
                    t.data.earlySpinDelaying = !0;
                    var a = N.quickStopCount,
                      n = N.isTurbo;
                    clearTimeout(t.earlySpinDelayingSetTimeout),
                      1 === a || n
                        ? (clearTimeout(t.earlySpinDelayingSetTimeout),
                          e.complete(),
                          (t.data.earlySpinDelaying = !1))
                        : (t.earlySpinDelayingSetTimeout = setTimeout(
                            function () {
                              e.complete(), (t.data.earlySpinDelaying = !1);
                            },
                            1875
                          ));
                  }),
                  this.on(m.SET_EARLY_SPIN_DELAYING_COMPLETED, function () {
                    t.earlySpinDelayingEvent &&
                      t.earlySpinDelayingEvent.complete();
                  }),
                  this.on(m.AUTO_SPIN_STATUS, function () {}),
                  this.once(S.SWIPE_UP, function () {
                    g.isComplete() &&
                      (App.gameAlert.isCurrentShow(u.TopErrorAlert) ||
                        App.gameLoading.complete());
                  }),
                  this.on(m.EARLY_DATA_PARSER_TO_SPIN_DATA, function () {
                    var e = t.data.earlyData;
                    Log.w("EARLY_DATA_PARSER_TO_SPIN_DATA::::", e),
                      (I.amount = e.platform.player.balance.amount),
                      null != e.platform.player.balance.betAmount &&
                        (I.betAmount = e.platform.player.balance.betAmount),
                      y.parseNewEarlySpin(e),
                      dispatch(S.UPDATE_USER_SPIN_ID, {
                        data: { spinId: e.engine.spinId },
                      });
                    var a = I.amount;
                    I.getData().theme &&
                      "xin-star" == I.getData().theme &&
                      (a = I.betAmount),
                      dispatch(S.UPDATE_USER_BALANCE, { data: { balance: a } }),
                      dispatch(m.PARSER_SPIN_COMPLETED);
                  }),
                  this.on(m.EARLY_CLOSE_DATA_PARSER_TO_DATA, function () {
                    var e = t.data.earlyCloseData;
                    (t.data.isEarlyCloseFlag = !1),
                      (I.amount = e.platform.player.balance.amount),
                      dispatch(S.UPDATE_USER_BALANCE, {
                        data: { balance: e.platform.player.balance.amount },
                      }),
                      dispatch(m.PARSER_CLOSE_SPIN_COMPLETED),
                      (t.data.earlyCloseData = null);
                  }),
                  this.on(m.WAIT_EARLY_DATA_RETRY, function (e) {
                    var a = 0;
                    t.data.waitEarlyDataRetryInterval = setInterval(
                      function () {
                        var n = t.data,
                          i = n.isEarlyFlag,
                          r = n.earlyData;
                        if (++a > 333) {
                          Log.e("EARLY_DATA timeout " + (30 * a) / 1e3 + "s"),
                            clearInterval(t.data.waitEarlyDataRetryInterval);
                          var o = {
                              text:
                                "early spin" +
                                App.getLanguage(
                                  "timeoutError",
                                  [],
                                  c[c.wrapper]
                                ),
                              confirmCb: function (t) {
                                l();
                              },
                              bbrCb: function (t) {},
                              needCloseAlert: !1,
                              code: "front",
                              tag: u.TopErrorAlert,
                            },
                            l = function () {
                              p.exit();
                            };
                          App.gameAlert.show(o, u.TopErrorAlert);
                        }
                        i &&
                          r &&
                          (e.complete(),
                          clearInterval(t.data.waitEarlyDataRetryInterval));
                      },
                      30
                    );
                  }),
                  this.on(m.WAIT_EARLY_SPIN_RESPONSE, function () {
                    null == t.data.earlyData &&
                      t.data.isOpenEarlyFlag &&
                      (t.earlyIntervalId = setInterval(function () {
                        t.data.earlyData &&
                          (clearInterval(t.earlyIntervalId),
                          dispatch(m.CREATE_SPIN_FLOW, {
                            data: { spinId: null, cheat: null, earlySpin: !0 },
                          }),
                          (t.earlyIntervalId = -1));
                      }, 100));
                  }),
                  this.on(m.KILL_WAIT_EARLY_DATA_RETRY_INTERVAL, function (e) {
                    clearInterval(t.data.waitEarlyDataRetryInterval);
                  }),
                  this.on(
                    m.KILL_WAIT_EARLY_CLOSE_DATA_RETRY_INTERVAL,
                    function (e) {
                      clearInterval(t.data.waitEarlyCloseDataRetryInterval);
                    }
                  ),
                  this.on(m.WAIT_EARLY_CLOSE_DATA_RETRY, function (e) {
                    var a = 0;
                    t.data.waitEarlyCloseDataRetryInterval = setInterval(
                      function () {
                        var n = t.data,
                          i = n.isEarlyCloseFlag,
                          r = n.earlyCloseData;
                        if ((a++, Log.d("wait close", a), a > 333)) {
                          Log.e(
                            "EARLY_CLOSE_DATA timeout " + (30 * a) / 1e3 + "s"
                          ),
                            clearInterval(
                              t.data.waitEarlyCloseDataRetryInterval
                            );
                          var o = {
                              text:
                                "early close" +
                                App.getLanguage(
                                  "timeoutError",
                                  [],
                                  c[c.wrapper]
                                ),
                              confirmCb: function (t) {
                                l();
                              },
                              bbrCb: function (t) {},
                              needCloseAlert: !1,
                              code: "front",
                              tag: u.TopErrorAlert,
                            },
                            l = function () {
                              p.exit();
                            };
                          App.gameAlert.show(o, u.TopErrorAlert);
                        }
                        i &&
                          r &&
                          (e.complete(),
                          clearInterval(
                            t.data.waitEarlyCloseDataRetryInterval
                          ));
                      },
                      30
                    );
                  }),
                  this.on(m.SHOW_BIGWIN, function (e) {
                    var i = e.data,
                      r = t.data.getData().parser.bigwinReach.level,
                      o = O.getData(),
                      l = o.smallPrizeDelay,
                      p = o.bigPrizeDelay,
                      d = i.isRoundWin ? 0 : r <= 3 ? l : p;
                    (App.globalAudio.isMusicOn = !1),
                      s(t)
                        .delay(d)
                        .call(
                          a(
                            n().mark(function t() {
                              return n().wrap(function (t) {
                                for (;;)
                                  switch ((t.prev = t.next)) {
                                    case 0:
                                      return (
                                        (App.globalAudio.isMusicOn = !0),
                                        (t.next = 3),
                                        App.uiManager.open({
                                          type: T,
                                          bundle: c[c.g1001],
                                          zIndex: u.UI,
                                          name: "BIG WIN",
                                        })
                                      );
                                    case 3:
                                      t.sent.showBigwin(e.complete, e.data);
                                    case 5:
                                    case "end":
                                      return t.stop();
                                  }
                              }, t);
                            })
                          )
                        )
                        .start();
                  }),
                  this.on(
                    m.SHOW_TREASURE_VIEW,
                    a(
                      n().mark(function t(e) {
                        return n().wrap(function (t) {
                          for (;;)
                            switch ((t.prev = t.next)) {
                              case 0:
                                return (
                                  App.globalAudio.pauseMusic(),
                                  (t.next = 3),
                                  App.uiManager.open({
                                    type: F,
                                    bundle: c[c.g1001],
                                    zIndex: u.UI,
                                    name: "BIG WIN",
                                  })
                                );
                              case 3:
                                t.sent.showTreasureWin(e.complete);
                              case 5:
                              case "end":
                                return t.stop();
                            }
                        }, t);
                      })
                    )
                  ),
                  this.on(m.SHOW_FG_INTRO_ALERT, function (t) {
                    App.uiManager
                      .open({
                        type: R,
                        bundle: c[c.g1001],
                        zIndex: u.UI,
                        name: "免費遊戲彈窗",
                      })
                      .then(function (t) {
                        t.showIntroAlert();
                      });
                  }),
                  this.on(m.SHOW_FG_SUMMARY_ALERT, function (t) {
                    App.uiManager
                      .open({
                        type: R,
                        bundle: c[c.g1001],
                        zIndex: u.UI,
                        name: "免費遊戲彈窗",
                      })
                      .then(function (e) {
                        e.showSummaryAlert(t.complete);
                      });
                  }),
                  this.on(
                    m.OPEN_FEATURE_POPUP,
                    a(
                      n().mark(function e(a) {
                        return n().wrap(function (e) {
                          for (;;)
                            switch ((e.prev = e.next)) {
                              case 0:
                                return (
                                  (e.next = 2),
                                  App.uiManager.open({
                                    type: D,
                                    bundle: t.bundle,
                                    zIndex: u.UI,
                                    name: "購買免費遊戲",
                                  })
                                );
                              case 2:
                                e.sent.openPopup();
                              case 4:
                              case "end":
                                return e.stop();
                            }
                        }, e);
                      })
                    )
                  ),
                  this.on(m.PARSER_REPLAY_COMPLETED, function (e) {
                    e ? t.view.initReplay() : t.view.againReplayUpdateAmount(),
                      dispatch(m.CREATE_REPLAY_FLOW);
                  }),
                  this.on(S.REPLAY_NEXT_SPIN, function () {
                    b.index++;
                    var e = b.index,
                      a = b.getData().betData.theResult[e];
                    t.data.setReplayCurrentView(a),
                      dispatch(m.CREATE_REPLAY_STOP_SPIN_FLOW);
                  }),
                  this.on(m.FG_START_COUNT_FOR_PLAY_LOG, function () {
                    t.fgPlayLogIntervalId = setInterval(function () {
                      dispatch(m.FG_UPDATE_SETTING_FOR_PLAY_LOG, {
                        type: "game",
                        data: {},
                      });
                    }, 3e4);
                  }),
                  this.on(m.FG_STOP_COUNT_FOR_PLAY_LOG, function () {
                    clearInterval(t.fgPlayLogIntervalId);
                  }),
                  this.on(m.PROCESS_REPLAY_IN_GAME, function (e) {
                    t.view.reset(),
                      s(t)
                        .delay(0.5)
                        .call(
                          a(
                            n().mark(function e() {
                              return n().wrap(function (e) {
                                for (;;)
                                  switch ((e.prev = e.next)) {
                                    case 0:
                                      return (
                                        (e.next = 2),
                                        App.uiManager.open({
                                          type: w,
                                          bundle: t.bundle,
                                          args: h.INIT_REPLAY,
                                        })
                                      );
                                    case 2:
                                    case "end":
                                      return e.stop();
                                  }
                              }, e);
                            })
                          )
                        )
                        .start();
                  }),
                  this.on(m.RESET_AND_OPEN_GAME_VIEW, function (e) {
                    b.reset();
                    var i = e.data;
                    t.view.reset(),
                      s(t)
                        .delay(0.5)
                        .call(
                          a(
                            n().mark(function e() {
                              return n().wrap(function (e) {
                                for (;;)
                                  switch ((e.prev = e.next)) {
                                    case 0:
                                      return (
                                        (e.next = 2),
                                        App.uiManager.open({
                                          type: w,
                                          bundle: t.bundle,
                                          args: i,
                                        })
                                      );
                                    case 2:
                                    case "end":
                                      return e.stop();
                                  }
                              }, e);
                            })
                          )
                        )
                        .start();
                  }),
                  this.on(m.SHAKE_NODE, function (e) {
                    t.view.shakeView();
                  }),
                  this.on(m.PLAY_BGM, function (e) {
                    t.view.playBGM(e.data);
                  }),
                  this.on(m.PLAY_BTM, function (e) {
                    var a = e.data,
                      n = a.url,
                      i = a.loop;
                    t.view.playBTM(n, i);
                  }),
                  this.on(m.STOP_BTM, function (e) {
                    t.view.stopBTM(e.data);
                  }),
                  this.on(m.MUSIC_VOLUME_MULTIPLE, function (e) {
                    t.view.mutipleMusicVolume(e.data);
                  }),
                  this.on(S.BUY_FEATURE_RESPONSE, function (e) {
                    t.view.buyFeatureSpin(e.data);
                  }),
                  this.on(m.REPLAY_START_QUICK_STOP, function () {
                    t.view.replayQuickStop();
                  });
              }),
              i(r, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(L);
                  },
                },
                {
                  key: "slotData",
                  get: function () {
                    return App.dataCenter.get(f);
                  },
                },
                {
                  key: "view",
                  get: function () {
                    return this.gameView;
                  },
                },
              ]),
              r
            );
          })(A)
        );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameSender.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./ServerModel.ts",
    "./CmmUtils.ts",
    "./Http.ts",
    "./SlotFrameworkEvent.ts",
    "./GameService.ts",
    "./type2.ts",
    "./Config.ts",
    "./GameSenderBase.ts",
    "./DefinitionModel.ts",
    "./GameStateModel.ts",
    "./InitialModel.ts",
    "./PlatformModel.ts",
    "./SettingsModel.ts",
    "./SlotTableModel.ts",
    "./SocketModel.ts",
    "./ReplayModel.ts",
    "./UrlUtils2.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./NoTouchingView.ts",
    "./SlotFrameworkData.ts",
  ],
  function (e) {
    "use strict";
    var t,
      s,
      a,
      n,
      o,
      r,
      i,
      u,
      S,
      l,
      d,
      c,
      E,
      p,
      R,
      f,
      T,
      g,
      A,
      _,
      h,
      m,
      O,
      v,
      L,
      C,
      N,
      P,
      D,
      w,
      I;
    return {
      setters: [
        function (e) {
          (t = e.inheritsLoose), (s = e.extends), (a = e.createClass);
        },
        function (e) {
          (n = e.cclegacy), (o = e.sys);
        },
        function (e) {
          r = e.EBundles;
        },
        function (e) {
          (i = e.default), (u = e.EServerMode);
        },
        function (e) {
          S = e.CmmUtils;
        },
        function (e) {
          l = e.Http;
        },
        function (e) {
          d = e.SlotFrameworkEvent;
        },
        function (e) {
          c = e.GameService;
        },
        function (e) {
          (E = e.ESocketRequestName),
            (p = e.ESpinStatus),
            (R = e.EDebugLogLevel);
        },
        function (e) {
          f = e.ViewZOrder;
        },
        function (e) {
          T = e.GameSenderBase;
        },
        function (e) {
          g = e.default;
        },
        function (e) {
          A = e.default;
        },
        function (e) {
          _ = e.default;
        },
        function (e) {
          h = e.default;
        },
        function (e) {
          m = e.default;
        },
        function (e) {
          O = e.default;
        },
        function (e) {
          v = e.default;
        },
        function (e) {
          (L = e.default), (C = e.EReplayMode);
        },
        function (e) {
          N = e.default;
        },
        function (e) {
          P = e.default;
        },
        function (e) {
          D = e.GameEvent;
        },
        function (e) {
          w = e.default;
        },
        function (e) {
          I = e.default;
        },
      ],
      execute: function () {
        n._RF.push({}, "be1dbC7O1BEpJuLAxYPjefm", "GameSender", void 0),
          (e(
            "GameSender",
            (function (e) {
              function n() {
                return e.apply(this, arguments) || this;
              }
              t(n, e);
              var T = n.prototype;
              return (
                (T.initial = function () {
                  var e = this;
                  if (i.mode !== u.STATIC) {
                    var t = {
                      token: v.currentToken,
                      clientType: S.getClientType(),
                      deviceInfo: {
                        browser: {
                          name: o.browserType,
                          version: o.browserVersion,
                        },
                        os: {
                          name: o.os,
                          version: o.osVersion,
                          versionName: o.osMainVersion,
                        },
                        platform: { type: o.platform },
                        engine: { name: "cocos creator 3.7.2" },
                      },
                    };
                    return new Promise(function (s, a) {
                      e.send("initial", t, function (t) {
                        if (t.status == l.ServerStatus.SUCCESS) {
                          if (t.code)
                            return (
                              Log.e("NETWORK_ERROR: ", t),
                              void e.responsShowAlert(
                                t.message,
                                null == t ? void 0 : t.code
                              )
                            );
                          try {
                            e.setToken(t),
                              g.setData(t.engine.definition),
                              A.setData(t.engine.gameState),
                              h.setData(t.platform),
                              m.setData(t.platform.player.settings),
                              _.setData(t),
                              dispatch(d.INIT_RESPONSE, t),
                              s();
                          } catch (e) {
                            var a = {
                              title: App.getLanguage(
                                "alertHint",
                                [],
                                r[r.slotFramework]
                              ),
                              text: "initial data error",
                              bbrCb: function () {},
                              needCloseAlert: !1,
                              code: e,
                            };
                            App.gameAlert.show(a);
                          }
                        } else Log.e("NETWORK_ERROR: ", t), e.responsShowAlert(t.message, null == t ? void 0 : t.code);
                      });
                    });
                  }
                }),
                (T.responsShowAlert = function (e, t) {
                  if ("xin-star" == h.getData().theme) {
                    var s = App.getLanguage(
                      "disconnectXinStar",
                      [],
                      r[r.wrapper]
                    );
                    this.showAlert(s, {
                      needCloseAlert: !1,
                      code: t,
                      titleisHidden: !0,
                      expandisHidden: !0,
                      confirmisHidden: !0,
                    });
                  } else this.showAlert(e, { needCloseAlert: !1, code: t });
                }),
                (T.spin = function (e, t, a, n) {
                  var o = this;
                  if (i.mode !== u.STATIC) {
                    var r = s(
                      { request: E.SPIN },
                      e,
                      { updateStake: n },
                      t && { spinId: t },
                      a && { cheat: a }
                    );
                    this.send(r.request, r, function (e) {
                      if (e.status == l.ServerStatus.SUCCESS)
                        o.setToken(e),
                          A.setData(e.engine.gameState),
                          (h.amount = e.platform.player.balance.amount),
                          null != e.platform.player.balance.betAmount &&
                            (h.betAmount = e.platform.player.balance.betAmount),
                          dispatch(d.SPIN_RESPONSE, e);
                      else if (e.status == l.ServerStatus.ERROR_SPIN_ONE_MORE) {
                        var s, a, n, i;
                        o.setToken(e),
                          dispatch(d.UPDATE_SPIN_STATUS, { data: p.IDLE }),
                          Log.e("後端->前端 多打了一次spin"),
                          o.debugLog({
                            id: t || o.data.getData().gameState.spinId,
                            level: R.ERROR,
                            message: "後端->前端 多打了一次spin",
                            data: {
                              requestVO: r,
                              currentData:
                                null == (s = o.data) ||
                                null == (a = s.getData())
                                  ? void 0
                                  : a.gameState,
                              preData:
                                null == (n = o.data) || null == (i = n.preData)
                                  ? void 0
                                  : i.gameState,
                            },
                          });
                      } else
                        Log.e("NETWORK_ERROR: ", e),
                          o.responsShowAlert(
                            e.message,
                            null == e ? void 0 : e.code
                          );
                    });
                  }
                }),
                (T.earlySpin = function (e, t, a, n) {
                  var o = this;
                  if (i.mode !== u.STATIC) {
                    var r = s(
                      { request: E.SPIN },
                      e,
                      { updateStake: a },
                      t && { spinId: t },
                      { forceClose: n }
                    );
                    Log.w("early request::::::::::", r, n),
                      this.send(r.request, r, function (e) {
                        e.status == l.ServerStatus.SUCCESS
                          ? (o.setToken(e), dispatch(d.EARLY_SPIN_RESPONSE, e))
                          : (Log.e("NETWORK_ERROR: ", e),
                            o.responsShowAlert(e.message, e.code));
                      });
                  }
                }),
                (T.closeSpin = function (e) {
                  var t = this,
                    s = { request: E.CLOSE_SPIN, spinId: e };
                  this.send(s.request, s, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (t.setToken(e),
                        (h.amount = e.platform.player.balance.amount),
                        dispatch(d.CLOSE_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        t.responsShowAlert(e.message, e.code));
                  });
                }),
                (T.earlyCloseSpin = function (e, t) {
                  var s = this,
                    a = { request: E.CLOSE_SPIN, spinId: e };
                  this.send(a.request, a, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (s.setToken(e),
                        t && t(),
                        dispatch(d.EARLY_CLOSE_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        s.responsShowAlert(e.message, e.code));
                  });
                }),
                (T.setting = function (e) {
                  var t = this,
                    a = s({ request: E.UPDATE_SETTINGS }, e);
                  this.send(a.request, a, function (e) {
                    if (e.status != l.ServerStatus.SUCCESS)
                      return (
                        Log.e("update setting NETWORK_ERROR: ", e),
                        void dispatch(D.FG_STOP_COUNT_FOR_PLAY_LOG)
                      );
                    t.setToken(e);
                  });
                }),
                (T.getBetRecords = function (e) {
                  var t = this,
                    a = s({ request: E.GET_BET_RECORDS }, e);
                  this.send(a.request, a, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (t.setToken(e), dispatch(d.BET_RECORDS_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        t.responsShowAlert(e.message, e.code));
                  });
                }),
                (T.getHistoryRecords = function (e) {
                  var t = this,
                    a = s({ request: E.GET_USER_REPORT }, e);
                  this.send(a.request, a, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (t.setToken(e), dispatch(d.GET_HISTORY_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        t.responsShowAlert(e.message, e.code));
                  });
                }),
                (T.getSlotTablePage = function (e) {
                  var t = this,
                    a = s({ request: E.GET_SLOT_TABLES }, e);
                  this.send(a.request, a, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (t.setToken(e),
                        O.setData(e),
                        dispatch(d.SLOT_TABLE_PAGE_DATA_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        t.responsShowAlert(e.message, e.code));
                  });
                }),
                (T.getSlotTableDetail = function (e) {
                  var t = this,
                    a = s({ request: E.GET_SLOT_TABLE_DETAIL }, e);
                  this.send(a.request, a, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (t.setToken(e),
                        O.setData(e),
                        dispatch(d.SLOT_TABLE_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        t.responsShowAlert(e.message, e.code));
                  });
                }),
                (T.changeSlotTable = function (e) {
                  var t = this,
                    a = s({ request: E.UPDATE_SLOT_TABLE }, e);
                  this.send(a.request, a, function (e) {
                    if (e.status !== l.ServerStatus.BACKEND_ERROR)
                      if (
                        (t.setToken(e),
                        e.status !== l.ServerStatus.NOT_MODIFIED)
                      ) {
                        var s = new URLSearchParams(window.location.search);
                        s.set("table", "1");
                        var a = window.location.pathname + "?" + s.toString();
                        window.location.href = a;
                      } else
                        App.gameAlert.show(
                          {
                            text: e.message,
                            confirmCb: function () {
                              dispatch(d.SYNC_SOLT_TABLES);
                            },
                            bbrCb: function () {},
                          },
                          f.TopErrorAlert
                        );
                    else
                      t.showAlert(e.message, {
                        needCloseAlert: !1,
                        code: e.code,
                      });
                  });
                }),
                (T.lockSlotTable = function (e) {
                  var t = this,
                    a = s({ request: E.LOCK_SLOT_TABLE }, e);
                  this.send(a.request, a, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (t.setToken(e), dispatch(d.LOCK_SLOT_TABLE_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        t.responsShowAlert(e.message, e.code));
                  });
                }),
                (T.buyFeature = function (e, t) {
                  var a = this,
                    n = s(
                      {
                        request: E.SPIN,
                        action: "buyFeature",
                        clientType: "web",
                        featureIndex: 0,
                        featureValue: "freeGame",
                      },
                      e,
                      { updateStake: !0 }
                    );
                  this.send(n.request, n, function (e) {
                    if (e.status == l.ServerStatus.SUCCESS)
                      a.setToken(e),
                        dispatch(d.BUY_FEATURE_RESPONSE, {
                          data: e.engine.gameState.spinId,
                        });
                    else if (
                      (Log.e("NETWORK_ERROR: ", e),
                      "xin-star" == h.getData().theme)
                    ) {
                      var t = App.getLanguage(
                        "disconnectXinStar",
                        [],
                        r[r.wrapper]
                      );
                      a.showAlert(t, {
                        needCloseAlert: !1,
                        code: e.code,
                        titleisHidden: !0,
                        expandisHidden: !0,
                        confirmisHidden: !0,
                      });
                    } else
                      App.gameAlert.show({
                        text: e.message,
                        confirmCb: function () {},
                        bbrCb: function () {},
                      });
                  });
                }),
                (T.updateAvatar = function (e) {
                  var t = { request: E.UPDATE_AVATAR, avatarId: e };
                  this.send(t.request, t),
                    (h.getData().player.avatar = e),
                    (h.getData().player.avatarUrl = N.GetAvatarUrl(e)),
                    dispatch(d.UPDATE_AVATAR_COMPLETED_RESPONSE);
                }),
                (T.updateDisplayName = function (e) {
                  var t = this,
                    s = { request: E.UPDATE_DISPLAYNAME, displayName: e };
                  this.send(s.request, s, function (s) {
                    t.setToken(s),
                      s.status !== l.ServerStatus.REQUEST_ERROR
                        ? ((h.getData().player.displayName = e),
                          dispatch(d.UPDATE_DISPLAYNAME_RESPONSE))
                        : dispatch(d.SET_DISPLAYNAME_TIP, s.message);
                  });
                }),
                (T.replay = function () {
                  var e = this,
                    t = new URL(window.location.href).searchParams.get(
                      "spinId"
                    ),
                    s = { request: E.REPLAY, spinId: t };
                  this.send(s.request, s, function (t) {
                    t.status == l.ServerStatus.SUCCESS
                      ? (L.setData(t),
                        g.setData(t.definition),
                        dispatch(d.REPLAY_RESPONSE, t))
                      : (Log.e("NETWORK_ERROR: ", t),
                        e.responsShowAlert(t.message));
                  });
                }),
                (T.getSlotBetRanksList = function (e) {
                  var t = this,
                    a = s(
                      { request: E.GET_SLOT_BET_RANKS_LIST, action: "list" },
                      e
                    );
                  this.send(a.request, a, function (e) {
                    e.status == l.ServerStatus.SUCCESS
                      ? (t.setToken(e),
                        dispatch(d.GET_RANKING_LIST_RESPONSE, e))
                      : (Log.e("NETWORK_ERROR: ", e),
                        t.showAlert(e.message, {
                          needCloseAlert: !1,
                          code: e.code,
                        }));
                  });
                }),
                (T.getSlotBetRanksReplay = function (e) {
                  var t = this,
                    a = s(
                      {
                        request: E.GET_SLOT_BET_RANKS_REPLAY,
                        action: "replay",
                      },
                      e
                    );
                  if (App.dataCenter.get(I).getData().spinStatus === p.IDLE)
                    return new Promise(function (e, s) {
                      t.send(a.request, a, function (s) {
                        (L.replayMode = C.RANKING_REPLAY),
                          s.status == l.ServerStatus.SUCCESS
                            ? ((L.isReplay = !0),
                              t.data.saveOriginGameData(),
                              L.setData(s),
                              (h.getData().player.displayName =
                                s.betData.replayMeta.displayName),
                              (h.amount = s.betData.replayMeta.amount),
                              s.definition && g.setData(s.definition),
                              dispatch(d.REPLAY_RESPONSE, s),
                              dispatch(D.PROCESS_REPLAY_IN_GAME, { data: s }),
                              e())
                            : (Log.e("NETWORK_ERROR: ", s),
                              t.showAlert(s.message, { needCloseAlert: !1 }));
                      });
                    });
                  App.uiManager.close(w);
                  var n = {
                    text: "請等待遊戲結束後，再進行重播",
                    confirmCb: function () {
                      dispatch(d.PLAY_CLICK_BTM);
                    },
                    bbrCb: function () {
                      dispatch(d.PLAY_CLICK_BTM);
                    },
                    needCloseAlert: !0,
                    tag: f.Tips,
                  };
                  App.gameAlert.show(n, f.Tips);
                }),
                a(n, [
                  {
                    key: "service",
                    get: function () {
                      return App.serviceManager.get(c);
                    },
                  },
                  {
                    key: "data",
                    get: function () {
                      return App.dataCenter.get(P);
                    },
                  },
                ]),
                n
              );
            })(T)
          ).module = r[r.g1001]),
          n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameService.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./GameServiceBase.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./res-type.ts",
  ],
  function (t) {
    "use strict";
    var a, e, n, s, o, i, r, c;
    return {
      setters: [
        function (t) {
          (a = t.inheritsLoose), (e = t.createClass);
        },
        function (t) {
          n = t.cclegacy;
        },
        function (t) {
          s = t.EBundles;
        },
        function (t) {
          o = t.GameServiceBase;
        },
        function (t) {
          i = t.default;
        },
        function (t) {
          r = t.SlotFrameworkEvent;
        },
        function (t) {
          c = t.ENotifyTypes;
        },
      ],
      execute: function () {
        n._RF.push({}, "5faa8MUgx9B67fN+efwp/6z", "GameService", void 0),
          (t(
            "GameService",
            (function (t) {
              function n() {
                return t.apply(this, arguments) || this;
              }
              return (
                a(n, t),
                (n.prototype.addSocketListeners = function () {
                  var t = this;
                  this.on("echo", function (t) {}),
                    this.on("warning", function (t) {
                      t.zip &&
                        1 == t.zip &&
                        (t.data
                          ? (t = JSON.parse(
                              pako.inflate(t.data, { to: "string" })
                            ))
                          : Log.e("no response data::::::::::::::::", t)),
                        dispatch(r.WARN_RESPONSE, t);
                    }),
                    this.on("error", function (t) {
                      t.zip &&
                        1 == t.zip &&
                        (t.data
                          ? (t = JSON.parse(
                              pako.inflate(t.data, { to: "string" })
                            ))
                          : Log.e("no response data::::::::::::::::", t)),
                        dispatch(r.ERROR_RESPONSE, t);
                    }),
                    this.on("notify", function (a) {
                      switch (
                        (a.zip &&
                          1 == a.zip &&
                          (a.data
                            ? (a = JSON.parse(
                                pako.inflate(a.data, { to: "string" })
                              ))
                            : Log.e("no response data::::::::::::::::", a)),
                        a.type)
                      ) {
                        case c.JACKPOT_UPDATE:
                          (t.slotData.tempJpPools = {
                            "jp-mini": a.data["jp-mini"],
                            "jp-minor": a.data["jp-minor"],
                            "jp-major": a.data["jp-major"],
                            "jp-grand": a.data["jp-grand"],
                          }),
                            dispatch(r.NOTIFY_JACKPOT_RESPONSE, { data: a });
                          break;
                        case c.SYSTEM:
                          dispatch(r.NOTIFY_SYSTEM_RESPONSE, { data: a });
                          break;
                        case c.JACKPOT_UPDATE:
                        case c.BIG_WIN:
                        case c.SUPER_WIN:
                        case c.MEGA_WIN:
                        case c.ULTRA_WIN:
                        case c.LEGENDARY_WIN:
                        case c.JP_MINI:
                        case c.JP_MINOR:
                        case c.JP_MAJOR:
                        case c.JP_GRAND:
                          dispatch(r.NOTIFY_PRIZE_RESPONSE, { data: a });
                      }
                    }),
                    this.on("slotTableUpdated", function (t) {
                      t.zip &&
                        1 == t.zip &&
                        (t.data
                          ? (t = JSON.parse(
                              pako.inflate(t.data, { to: "string" })
                            ))
                          : Log.e("no response data::::::::::::::::", t)),
                        dispatch(r.SLOT_TABLES_UPDATED_RESPONSE, t);
                    });
                }),
                e(n, [
                  {
                    key: "slotData",
                    get: function () {
                      return App.dataCenter.get(i);
                    },
                  },
                ]),
                n
              );
            })(o)
          ).module = s[s.g1001]),
          n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameSymbolID.ts",
  ["cc", "./UrlUtils.ts"],
  function (M) {
    "use strict";
    var S, t, e;
    return {
      setters: [
        function (M) {
          (S = M.cclegacy), (t = M.Vec3);
        },
        function (M) {
          e = M.default;
        },
      ],
      execute: function () {
        var E, s, A, n;
        M({
          EBackendSymbolID: void 0,
          EReelStatus: void 0,
          ESymbolAnimType: void 0,
          ESymbolStatus: void 0,
        }),
          S._RF.push({}, "7a03bxdEEpBMrPhnQkNvMzu", "GameSymbolID", void 0),
          (function (M) {
            (M[(M.BLUR = 0)] = "BLUR"),
              (M[(M.STATIC = 1)] = "STATIC"),
              (M[(M.ANIM = 2)] = "ANIM"),
              (M[(M.WIN = 3)] = "WIN");
          })(E || (E = M("ESymbolStatus", {}))),
          (function (M) {
            (M.LOOP = "loop"),
              (M.WIN = "win"),
              (M.IN = "in"),
              (M.OUT = "out"),
              (M.TEASE = "tease"),
              (M.FUNCTION = "function");
          })(s || (s = M("ESymbolAnimType", {}))),
          (function (M) {
            (M.SPINNING = "SPINNING"),
              (M.STOPPING = "STOPPING"),
              (M.STATIC = "STATIC");
          })(A || (A = M("EReelStatus", {}))),
          (function (M) {
            (M[(M.EYE = 1)] = "EYE"),
              (M[(M.SNAKE = 2)] = "SNAKE"),
              (M[(M.BOW = 3)] = "BOW"),
              (M[(M.MACHETE = 4)] = "MACHETE"),
              (M[(M.ORANGE_GEM = 5)] = "ORANGE_GEM"),
              (M[(M.RED_GEM = 6)] = "RED_GEM"),
              (M[(M.PURPLE_GEM = 7)] = "PURPLE_GEM"),
              (M[(M.BLUE_GEM = 8)] = "BLUE_GEM"),
              (M[(M.GREEN_GEM = 9)] = "GREEN_GEM"),
              (M[(M.T1 = 10)] = "T1"),
              (M[(M.T2 = 11)] = "T2"),
              (M[(M.T3 = 12)] = "T3"),
              (M[(M.T4 = 13)] = "T4"),
              (M[(M.JACKPOT = 14)] = "JACKPOT"),
              (M[(M.SCATTER = 15)] = "SCATTER");
          })(n || (n = M("EBackendSymbolID", {})));
        var o = M(
          "GameSymbolID",
          (function () {
            function M() {}
            return (
              (M.init = function () {
                this.mapSymbolAnims(),
                  this.makeSymbolPosConfig(e.getViewModeParam());
              }),
              (M.mapSymbolAnims = function () {
                var S = s.FUNCTION,
                  t = s.WIN,
                  e = s.IN,
                  E = s.LOOP;
                M.SYMBOL_ANIMS_MAP.set(n.EYE, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.SNAKE, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.BOW, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.MACHETE, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.ORANGE_GEM, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.RED_GEM, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.PURPLE_GEM, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.BLUE_GEM, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.GREEN_GEM, [t]),
                  M.SYMBOL_ANIMS_MAP.set(n.T1, [S]),
                  M.SYMBOL_ANIMS_MAP.set(n.T2, [S]),
                  M.SYMBOL_ANIMS_MAP.set(n.T3, [S]),
                  M.SYMBOL_ANIMS_MAP.set(n.T4, [S]),
                  M.SYMBOL_ANIMS_MAP.set(n.JACKPOT, [e, E, t]),
                  M.SYMBOL_ANIMS_MAP.set(n.SCATTER, [e, t]);
              }),
              (M.makeSymbolPosConfig = function (M) {
                void 0 === M && (M = "landscape"),
                  Log.e("make symbol position config::::", M);
                for (
                  var S = "landscape" == M ? 375 : 353,
                    e = "landscape" == M ? 250 : 235,
                    E = "landscape" == M ? this.SYMBOL_WIDTH : 117,
                    s =
                      "landscape" == M
                        ? this.SYMBOL_HIGH
                        : 0.94 * this.SYMBOL_HIGH,
                    A = "landscape" == M ? 64 : 60,
                    n = "landscape" == M ? -54 : -51,
                    o = 0;
                  o < this.TOTAL_SYMBOL;
                  o++
                ) {
                  var _ = new t(0, 0);
                  (_.x = A + (o % this.ROW) * (E + 0) - S),
                    (_.y = n + Math.floor(o / this.ROW) * -(s + 0) + e),
                    this.symbolPosConfig.set(o, _);
                }
              }),
              M
            );
          })()
        );
        (o.ROW = 6),
          (o.COL = 5),
          (o.TOTAL_SYMBOL = o.ROW * o.COL),
          (o.SYMBOL_WIDTH = 124),
          (o.SYMBOL_HIGH = 98),
          (o.symbolPosConfig = new Map()),
          (o.SYMBOL_ANIMS_MAP = new Map()),
          (o.symbolTextures = []),
          (o.symbolSpriteMap = new Map()),
          (o.symbolAnimMap = new Map()),
          S._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/GameView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Config.ts",
    "./Bundles.ts",
    "./CmmUtils.ts",
    "./AdapterEvent.ts",
    "./GameViewBase.ts",
    "./Decorators.ts",
    "./WrapperData.ts",
    "./PrizeNotify.ts",
    "./InfoBarController.ts",
    "./InfoBarPController.ts",
    "./MenuController.ts",
    "./SpinBarControllerLandScape.ts",
    "./SpinBarPController.ts",
    "./TopBar.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./PlatformModel.ts",
    "./ReplayModel.ts",
    "./SettingsModel.ts",
    "./type2.ts",
    "./CmmSlotUtils.ts",
    "./LoadUtils.ts",
    "./SlotTableViewL.ts",
    "./SlotTableViewP.ts",
    "./ReplayUIViewL.ts",
    "./ReplayUIViewP.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./GameLogic.ts",
    "./SlotTableViewL_v2.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var e,
      n,
      a,
      i,
      o,
      r,
      s,
      l,
      u,
      p,
      c,
      d,
      f,
      h,
      g,
      m,
      b,
      _,
      S,
      y,
      A,
      E,
      I,
      C,
      v,
      D,
      T,
      w,
      P,
      B,
      L,
      U,
      N,
      M,
      R,
      V,
      O,
      G,
      k,
      F,
      z,
      x,
      W,
      H,
      Y,
      Q,
      j,
      q,
      K,
      J,
      Z,
      X,
      $,
      tt,
      et;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (n = t.inheritsLoose),
            (a = t.initializerDefineProperty),
            (i = t.assertThisInitialized),
            (o = t.createClass),
            (r = t.asyncToGenerator),
            (s = t.regeneratorRuntime);
        },
        function (t) {
          (l = t.cclegacy),
            (u = t._decorator),
            (p = t.NodeEventType),
            (c = t.Size),
            (d = t.UITransform),
            (f = t.instantiate),
            (h = t.Widget),
            (g = t.Vec3),
            (m = t.Input),
            (b = t.tween),
            (_ = t.Color),
            (S = t.game),
            (y = t.Node);
        },
        function (t) {
          A = t.ViewZOrder;
        },
        function (t) {
          E = t.EBundles;
        },
        function (t) {
          I = t.CmmUtils;
        },
        function (t) {
          C = t.EOrientationType;
        },
        function (t) {
          v = t.default;
        },
        function (t) {
          D = t.inject;
        },
        function (t) {
          T = t.default;
        },
        function (t) {
          w = t.PrizeNotify;
        },
        function (t) {
          P = t.default;
        },
        function (t) {
          B = t.default;
        },
        function (t) {
          L = t.default;
        },
        function (t) {
          U = t.default;
        },
        function (t) {
          N = t.default;
        },
        function (t) {
          M = t.default;
        },
        function (t) {
          R = t.default;
        },
        function (t) {
          V = t.SlotFrameworkEvent;
        },
        function (t) {
          O = t.default;
        },
        function (t) {
          G = t.default;
        },
        function (t) {
          k = t.default;
        },
        function (t) {
          F = t.ESpinStatus;
        },
        function (t) {
          z = t.CmmSlotUtils;
        },
        function (t) {
          x = t.LoadUtils;
        },
        function (t) {
          W = t.default;
        },
        function (t) {
          H = t.default;
        },
        function (t) {
          Y = t.default;
        },
        function (t) {
          Q = t.default;
        },
        function (t) {
          (j = t.default), (q = t.EBTM), (K = t.EBGM);
        },
        function (t) {
          (J = t.default), (Z = t.EInitName);
        },
        function (t) {
          X = t.GameEvent;
        },
        function (t) {
          $ = t.GameLogic;
        },
        function (t) {
          tt = t.default;
        },
        function (t) {
          et = t.default;
        },
      ],
      execute: function () {
        var nt,
          at,
          it,
          ot,
          rt,
          st,
          lt,
          ut,
          pt,
          ct,
          dt,
          ft,
          ht,
          gt,
          mt,
          bt,
          _t,
          St;
        l._RF.push({}, "94978i7nIVIwZCtkj9L5W1h", "GameView", void 0);
        var yt = u.ccclass;
        u.property,
          t(
            "default",
            ((nt = yt("GameView")),
            (at = D("content", y)),
            (it = D("content/gameLayer", y)),
            (ot = D("content/uiLayer", y)),
            (rt = D("content/uiLayer/leftContent", y)),
            (st = D("content/gameLayer/ReelView", y)),
            (lt = D("content/gameLayer/SymbolView", y)),
            (ut = D("content/uiLayer/rotateScreenBtn", y)),
            nt(
              (((St = (function (t) {
                function e() {
                  for (
                    var e, n = arguments.length, o = new Array(n), r = 0;
                    r < n;
                    r++
                  )
                    o[r] = arguments[r];
                  return (
                    (e = t.call.apply(t, [this].concat(o)) || this),
                    a(e, "content", dt, i(e)),
                    a(e, "gameLayer", ft, i(e)),
                    a(e, "uiLayer", ht, i(e)),
                    a(e, "leftContent", gt, i(e)),
                    a(e, "ReelView", mt, i(e)),
                    a(e, "SymbolView", bt, i(e)),
                    a(e, "rotateScreenBtn", _t, i(e)),
                    (e.slotUIConfigs = []),
                    (e.slotUIMap = new Map()),
                    e
                  );
                }
                n(e, t);
                var l = e.prototype;
                return (
                  (l.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (l.start = function () {
                    this.beforeInit();
                  }),
                  (l.onDestroy = function () {
                    this.removeAllEvents();
                  }),
                  (e.getPrefabUrl = function () {
                    return "prefabs/" + et.getViewModeParam() + "/GameView";
                  }),
                  (l.reset = function () {
                    t.prototype.reset.call(this);
                  }),
                  (l.beforeInit = (function () {
                    var t = r(
                      s().mark(function t() {
                        var e;
                        return s().wrap(
                          function (t) {
                            for (;;)
                              switch ((t.prev = t.next)) {
                                case 0:
                                  if ((e = this.args)) {
                                    t.next = 3;
                                    break;
                                  }
                                  return t.abrupt("return");
                                case 3:
                                  e === Z.INIT_REPLAY
                                    ? (!0,
                                      dispatch(X.PARSER_REPLAY_COMPLETED, true),
                                      dispatch(V.UPDATE_USER_SPIN_ID, {
                                        data: { spinId: "" },
                                      }),
                                      this.playBGM(K.MAINGAME))
                                    : e == Z.INIT_GAME &&
                                      ((G.isReplay = !1),
                                      j.setIsTurbo(
                                        O.getData().player.settings
                                          .advancedSettings.turbo
                                      ),
                                      dispatch(
                                        V.CLICK_GAME_LOADING_CONFIRM_BTN
                                      ));
                                case 4:
                                case "end":
                                  return t.stop();
                              }
                          },
                          t,
                          this
                        );
                      })
                    );
                    return function () {
                      return t.apply(this, arguments);
                    };
                  })()),
                  (l.init = function () {
                    this.initGameViewSize(),
                      this.initNewCompleted(),
                      this.setUI(),
                      this.initAudio(),
                      this.setEventTouch(),
                      this.gameLayer.on(p.TOUCH_END, this.quickStop, this),
                      this.initRotateScreenBtn();
                  }),
                  (l.initRotateScreenBtn = function () {
                    var t = O.getData().disableRotate,
                      e = void 0 !== t && t;
                    0 == e &&
                      (e =
                        null == et.getParam("disableRotate")
                          ? e
                          : Boolean(et.getParam("disableRotate"))),
                      (this.rotateScreenBtn.active = 1 != e);
                  }),
                  (l.initReplay = function () {
                    this.setReplayUI(),
                      this.initAudio(),
                      this.gameLayer.on(
                        p.TOUCH_END,
                        this.replayQuickStop,
                        this
                      ),
                      (O.getData().player.avatarUrl =
                        G.getData().betData.replayMeta.avatarUrl),
                      (O.getData().player.displayName =
                        G.getData().betData.replayMeta.displayName),
                      dispatch(V.UPDATE_USER_BALANCE, {
                        data: {
                          balance: G.getData().betData.replayMeta.amount,
                        },
                      }),
                      dispatch(V.UPDATE_AVATAR_COMPLETED_RESPONSE),
                      dispatch(V.SET_DISPLAY_NAME),
                      dispatch(V.UPDATE_USER_SPIN_ID, { data: { spinId: "" } });
                  }),
                  (l.againReplayUpdateAmount = function () {
                    dispatch(X.UPDATE_WIN_AMOUNT, { data: { value: 0 } }),
                      dispatch(V.UPDATE_TOTAL_WINNINGS, { data: { value: 0 } });
                  }),
                  (l.initGameViewSize = function () {
                    var t =
                      this.wrapperData.orientation === C.LANDSCAPE
                        ? new c(1280, 720)
                        : new c(720, 1280);
                    this.content.getComponent(d).setContentSize(t);
                  }),
                  (l.createBuyFeatureBtn = function () {
                    var t = j.getData().filePaths.buyFeatureBtnPrefab,
                      e = this.data.getData().definition.buyFeature,
                      n = App.cache.get(this.data.module, t).data;
                    if (e.length > 0) {
                      var a = f(n);
                      this.uiLayer.addChild(a);
                    }
                  }),
                  (l.setReplayUI = function () {
                    var t = this.slotData.getData().filePaths,
                      e = t.infoBarPPrefab,
                      n = t.infoBarPrefab,
                      a = (t.spinBarPPrefab, t.spinBarPrefab);
                    (this.slotUIConfigs = [
                      {
                        path: z.getOrientationTarget(n, e),
                        component: z.getOrientationTarget(P, B),
                      },
                      {
                        path: z.getOrientationTarget(
                          "prefabs/ui/topBar/TopBar",
                          "prefabs/ui/topBar/TopBarP"
                        ),
                        component: M,
                      },
                    ]),
                      "landscape" == et.getViewModeParam() &&
                        this.slotUIConfigs.push({ path: a, component: U }),
                      this.addSlotUI(this.slotUIConfigs);
                    var i = z.getOrientationTarget(Y, Q);
                    App.uiManager.open({
                      type: i,
                      bundle: E[E.slotFramework],
                      zIndex: A.ReplayUI,
                      name: "replay UI層",
                    }),
                      this.uiLayer
                        .getComponentInChildren(M)
                        .setVersion("v" + this.data.GAME_VERSION),
                      this.initRotateScreenBtn();
                  }),
                  (l.setUI = function () {
                    var t = this.slotData.getData().filePaths,
                      e = t.infoBarPPrefab,
                      n = t.infoBarPrefab,
                      a = t.spinBarPPrefab,
                      i = t.spinBarPrefab;
                    (this.slotUIConfigs = [
                      {
                        path: z.getOrientationTarget(n, e),
                        component: z.getOrientationTarget(P, B),
                      },
                      {
                        path: z.getOrientationTarget(i, a),
                        component: z.getOrientationTarget(U, N),
                      },
                      {
                        path: z.getOrientationTarget(
                          "prefabs/ui/topBar/TopBar",
                          "prefabs/ui/topBar/TopBarP"
                        ),
                        component: M,
                      },
                      { path: "prefabs/component/PrizeNotify", component: w },
                    ]),
                      this.addSlotUI(this.slotUIConfigs),
                      this.setSlotUIData();
                  }),
                  (l.addSlotUI = function (t) {
                    var e = this;
                    t.forEach(function (t) {
                      var n = t.path,
                        a = t.component,
                        i = App.cache.get(E[E.slotFramework], n).data,
                        o = f(i);
                      e.slotUIMap.set(o.name, o),
                        o.addComponent(a),
                        e.uiLayer.addChild(o);
                    });
                    var n = this.uiLayer.getComponentInChildren(w);
                    if (n) {
                      var a = et.getViewModeParam(),
                        i = n.node.getChildByName("content").getComponent(h);
                      "landscape" == a
                        ? ((i.left = 0),
                          (i.isAlignVerticalCenter = !0),
                          (i.verticalCenter = -50),
                          (n.node.active = !0))
                        : ((i.left = -14),
                          (i.isAbsoluteLeft = !0),
                          (i.isAlignVerticalCenter = !0),
                          (i.verticalCenter = 310),
                          (n.node.active = !0));
                    }
                  }),
                  (l.setSlotUIData = function () {
                    var t = this;
                    if (App.dataCenter.get(T).orientation === C.LANDSCAPE) {
                      var e = this.uiLayer.getComponentInChildren(U);
                      e.addSpinEventTouch(this.name, function () {
                        t.spin();
                      }),
                        e.addQuickStopEventTouch(function () {
                          t.quickStop();
                        }),
                        e.initTurbo(j.isTurbo),
                        e.addTurboEventTouch(j);
                      var n = j.getData().filePaths,
                        a = n.common,
                        i = n.font,
                        o = n.localeSpriteFrame,
                        r = n.spinSkeleton,
                        s = App.cache.get(E[E.g1001], r).data[0],
                        l = {
                          normal: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_bg_normal"
                          ),
                          pressed: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_bg_pressed"
                          ),
                          hover: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_bg_normal"
                          ),
                          disabled: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_bg_disabled"
                          ),
                        },
                        u = {
                          normal: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_icon_normal"
                          ),
                          pressed: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_icon_pressed"
                          ),
                          hover: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_icon_normal"
                          ),
                          disabled: x.getDirSp(
                            this.bundle,
                            a,
                            "mg_btn_spin_icon_disabled"
                          ),
                        },
                        p = {
                          font: x.getDirSp(this.bundle, i, "countup_01"),
                          fontSize: 8,
                          fontPos: new g(0, 12, 0),
                        };
                      e.setSpinBtnData(s, l, u, p);
                      var c = this.uiLayer.getComponentInChildren(M);
                      c.setVersion("v" + this.data.GAME_VERSION);
                      var d = O.getData().jackpotOn;
                      c.showHideJPBar(d);
                      var f = c.getComponentInChildren(L),
                        h = { bundle: this.bundle, background: a, rules: o };
                      O.getData().theme &&
                        "xin-star" == O.getData().theme &&
                        (h.excludeIndexes = [6, 7]),
                        f.setRuleAssets(h);
                    } else {
                      var m = this.uiLayer.getComponentInChildren(N);
                      m.addSpinEventTouch(this.name, function () {
                        t.spin();
                      }),
                        m.addQuickStopEventTouch(function () {
                          t.quickStop();
                        }),
                        m.initTurbo(j.isTurbo),
                        m.addTurboEventTouch(j);
                      var b = j.getData().filePaths,
                        _ = b.common,
                        S = b.font,
                        y = b.localeSpriteFrame,
                        A = b.spinSkeleton,
                        I = App.cache.get(E[E.g1001], A).data[0],
                        v = {
                          normal: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_bg_normal"
                          ),
                          pressed: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_bg_pressed"
                          ),
                          hover: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_bg_normal"
                          ),
                          disabled: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_bg_disabled"
                          ),
                        },
                        D = {
                          normal: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_icon_normal"
                          ),
                          pressed: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_icon_pressed"
                          ),
                          hover: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_icon_normal"
                          ),
                          disabled: x.getDirSp(
                            this.bundle,
                            _,
                            "mg_btn_spin_icon_disabled"
                          ),
                        },
                        w = {
                          font: x.getDirSp(this.bundle, S, "countup_01"),
                          fontSize: 8,
                          fontPos: new g(0, 12, 0),
                        };
                      m.setSpinBtnData(I, v, D, w);
                      var P = this.uiLayer.getComponentInChildren(M);
                      P.setVersion("v" + this.data.GAME_VERSION);
                      var B = O.getData().jackpotOn;
                      P.showHideJPBar(B);
                      P.getComponentInChildren(L);
                      var R = { bundle: this.bundle, background: _, rules: y };
                      O.getData().theme &&
                        "xin-star" == O.getData().theme &&
                        (R.excludeIndexes = [6, 7]),
                        m.setRuleAssets(R);
                    }
                  }),
                  (l.setEventTouch = function () {
                    this.onI(m.EventType.KEY_DOWN, function (t) {
                      t.keyCode;
                    });
                  }),
                  (l.shakeView = function () {
                    var t = this,
                      e = 0.02;
                    [this.ReelView, this.SymbolView].forEach(function (n) {
                      b(n)
                        .delay(0.3)
                        .to(e, { position: new g(18, 21, 0) })
                        .to(e, { position: new g(39, 9, 0) })
                        .to(e, { position: new g(-9, -18, 0) })
                        .to(e, { position: new g(15, 15, 0) })
                        .to(e, { position: new g(-6, -24, 0) })
                        .to(e, { position: new g(24, -30, 0) })
                        .to(e, { position: new g(-9, 30, 0) })
                        .to(e, { position: new g(9, -15, 0) })
                        .to(e, { position: new g(-12, 24, 0) })
                        .to(e, { position: new g(0, 0, 0) })
                        .call(function () {
                          t.node.position = new g(0, 0, 0);
                        })
                        .start();
                    });
                  }),
                  (l.playBGM = function (t) {
                    this.audioHelper.playMusic(t, this.bundle);
                  }),
                  (l.playBTM = function (t, e) {
                    void 0 === e && (e = !1),
                      this.audioHelper.playEffect(t, this.bundle, e);
                  }),
                  (l.stopBTM = function (t) {
                    this.audioHelper.stopEffect(t, this.bundle);
                  }),
                  (l.initAudio = function () {
                    var t, e;
                    if (et.hasParam("spinId"))
                      return (
                        (App.globalAudio.musicVolume = 0),
                        void (App.globalAudio.effectVolume = 0)
                      );
                    (App.globalAudio.musicVolume =
                      null != (t = k.backgroundVolume) ? t : 1),
                      (App.globalAudio.effectVolume =
                        null != (e = k.effectVolume) ? e : 1);
                  }),
                  (l.buyFeatureSpin = function (t) {
                    dispatch(X.CLOSE_FEATURE_POPUP),
                      dispatch(X.CREATE_SPIN_FLOW, {
                        data: { spinId: t, cheat: null },
                      }),
                      dispatch(X.UPDATE_WIN_AMOUNT, { data: { value: 0 } }),
                      dispatch(V.UPDATE_TOTAL_WINNINGS, { data: { value: 0 } }),
                      this.playBTM(q.SPIN);
                  }),
                  (l.showResumeAlert = function () {
                    var t = {
                      text: App.getLanguage("wrapper1", [], E[E.wrapper]),
                      bbrColor: new _(0, 0, 0, 255),
                      confirmCb: function (t) {
                        dispatch(X.CREATE_RESUME_FLOW);
                      },
                    };
                    App.gameAlert.show(t);
                    var e = "egyptian-mythology" === et.getParam("gn") ? tt : W;
                    App.uiManager.close(z.getOrientationTarget(e, H));
                  }),
                  (l.cheat = function (t) {
                    dispatch(X.CREATE_SPIN_FLOW, {
                      data: { spinId: null, cheat: t },
                    });
                  }),
                  (l.spin = function () {
                    var t = I.extractContentBetweenAngleBrackets(this.name)[0];
                    App.uiManager.IsOnlyGameViewOpen(t) &&
                      (dispatch(X.CREATE_SPIN_FLOW, {
                        data: { spinId: null, cheat: null },
                      }),
                      this.playBTM(q.SPIN));
                  }),
                  (l.quickStop = function () {
                    var t = App.dataCenter.get(R).getData().spinStatus,
                      e = I.extractContentBetweenAngleBrackets(this.name)[0],
                      n = App.uiManager.IsOnlyGameViewOpen(e);
                    t === F.SPINING && n && dispatch(X.CREATE_QUICK_STOP_FLOW);
                  }),
                  (l.replayQuickStop = function () {
                    var t = App.dataCenter.get(R).getData().spinStatus;
                    S.isPaused() ||
                      (t === F.SPINING &&
                        dispatch(X.CREATE_REPLAY_QUICK_STOP_FLOW));
                  }),
                  (l.mutipleMusicVolume = function (t) {
                    App.globalAudio.musicVolume =
                      App.globalAudio.musicVolume * t;
                  }),
                  (l.initNewCompleted = function () {
                    var t = this.data.getData().isResuming,
                      e =
                        "spin" ==
                        this.data.getData().newGameState[
                          this.data.currSpinIndex
                        ].action,
                      n = e ? K.MAINGAME : K.FREEGAME;
                    this.createBuyFeatureBtn(),
                      t
                        ? (this.playBGM(n),
                          dispatch(X.CHANGE_GAME_STYLE, { data: e }),
                          this.showResumeAlert())
                        : (this.playBGM(K.MAINGAME),
                          dispatch(X.CHANGE_GAME_STYLE, { data: !0 }));
                  }),
                  (l.showCheat = function () {
                    this.leftContent.active = !this.leftContent.active;
                  }),
                  o(e, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(J);
                      },
                    },
                    {
                      key: "slotData",
                      get: function () {
                        return App.dataCenter.get(R);
                      },
                    },
                    {
                      key: "wrapperData",
                      get: function () {
                        return App.dataCenter.get(T);
                      },
                    },
                  ]),
                  e
                );
              })(v)).logicType = $),
              (dt = e((ct = St).prototype, "content", [at], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (ft = e(ct.prototype, "gameLayer", [it], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (ht = e(ct.prototype, "uiLayer", [ot], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (gt = e(ct.prototype, "leftContent", [rt], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (mt = e(ct.prototype, "ReelView", [st], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (bt = e(ct.prototype, "SymbolView", [lt], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (_t = e(ct.prototype, "rotateScreenBtn", [ut], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (pt = ct))
            ) || pt)
          );
        l._RF.pop();
      },
    };
  }
);

System.register("chunks:///_virtual/GlobalModel.ts", ["cc"], function (e) {
  "use strict";
  var t;
  return {
    setters: [
      function (e) {
        t = e.cclegacy;
      },
    ],
    execute: function () {
      t._RF.push({}, "02706LVlg5PQZAgKVgWY6Yo", "GlobalModel", void 0);
      var n = e(
        "GlobalModel",
        (function () {
          function e() {}
          return (
            (e.GetCurrSpinData = function () {
              return (
                (e.GameStates &&
                  e.GameStates.length > 0 &&
                  e.GameStates[e.currSpinIndex]) ||
                null
              );
            }),
            e
          );
        })()
      );
      (n.InitialResponse = void 0),
        (n.GameStates = []),
        (n.Platform = void 0),
        (n.SpinResponse = void 0),
        (n.currSpinIndex = 0),
        (n.isInit = !1),
        t._RF.pop();
    },
  };
});

System.register(
  "chunks:///_virtual/IntroView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Bundles.ts",
    "./CmmUtils.ts",
    "./UIView.ts",
    "./Decorators.ts",
    "./SlotFrameworkEvent.ts",
    "./LoadUtils.ts",
    "./MathUtil.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var e,
      n,
      i,
      r,
      o,
      a,
      s,
      l,
      u,
      c,
      p,
      f,
      g,
      h,
      m,
      d,
      w,
      b,
      S,
      v,
      y,
      P,
      T,
      A,
      V;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (n = t.inheritsLoose),
            (i = t.initializerDefineProperty),
            (r = t.assertThisInitialized),
            (o = t.createClass);
        },
        function (t) {
          (a = t.cclegacy),
            (s = t._decorator),
            (l = t.UIOpacity),
            (u = t.tween),
            (c = t.NodeEventType),
            (p = t.Sprite),
            (f = t.sp),
            (g = t.PageView),
            (h = t.Node),
            (m = t.Button);
        },
        function (t) {
          d = t.EBundles;
        },
        function (t) {
          w = t.CmmUtils;
        },
        function (t) {
          b = t.default;
        },
        function (t) {
          S = t.inject;
        },
        function (t) {
          v = t.SlotFrameworkEvent;
        },
        function (t) {
          y = t.LoadUtils;
        },
        function (t) {
          P = t.default;
        },
        function (t) {
          T = t.default;
        },
        function (t) {
          A = t.default;
        },
        function (t) {
          V = t.default;
        },
      ],
      execute: function () {
        var C, I, x, D, L, G, _, F, N, U, z, k, E, B, M, R, O;
        a._RF.push({}, "8c7824k7QRNDqAv/qnjGzUQ", "IntroView", void 0);
        var j = s.ccclass;
        s.property,
          t(
            "IntroView",
            ((C = j("IntroView")),
            (I = S("pageView", g)),
            (x = S("bbr", h)),
            (D = S("startGame", h)),
            (L = S("gameLogo", p)),
            (G = S("leftArrow", m)),
            (_ = S("rightArrow", m)),
            (F = S("introTextArea/text", p)),
            C(
              ((z = e(
                (U = (function (t) {
                  function e() {
                    for (
                      var e, n = arguments.length, o = new Array(n), a = 0;
                      a < n;
                      a++
                    )
                      o[a] = arguments[a];
                    return (
                      (e = t.call.apply(t, [this].concat(o)) || this),
                      i(e, "pageView", z, r(e)),
                      i(e, "bbr", k, r(e)),
                      i(e, "startGame", E, r(e)),
                      i(e, "gameLogo", B, r(e)),
                      i(e, "leftArrow", M, r(e)),
                      i(e, "rightArrow", R, r(e)),
                      i(e, "infoTextSprite", O, r(e)),
                      (e.spineNodes = []),
                      e
                    );
                  }
                  n(e, t);
                  var a = e.prototype;
                  return (
                    (a.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (a.start = function () {
                      var t = this;
                      this.init(),
                        this.setInfoTextSprite(0),
                        this.playSpineAnim(0),
                        this.pageView.node.on(
                          "page-turning",
                          this.onPageTurning,
                          this
                        ),
                        w.addBtnClickEvent(this.leftArrow.node, function () {
                          t.onPrevPage();
                        }),
                        w.addBtnClickEvent(this.rightArrow.node, function () {
                          t.onNextPage();
                        });
                    }),
                    (a.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (e.getPrefabUrl = function () {
                      return "prefabs/" + V.getViewModeParam() + "/IntroView";
                    }),
                    (a.init = function () {
                      this.setGameLogo(),
                        this.setStartGame(),
                        this.setPageSpines(),
                        w.fadeInTween(this.node, 0.1);
                    }),
                    (a.setGameLogo = function () {
                      var t = T.getData().filePaths.localeSpriteFrame;
                      this.gameLogo.spriteFrame = y.getDirSp(
                        d[d.g1001],
                        t,
                        "l_logo"
                      );
                    }),
                    (a.setStartGame = function () {
                      var t = this,
                        e = T.getData().filePaths.localeSpriteFrame,
                        n = this.startGame.getComponent(l);
                      (n.opacity = 0),
                        u(n)
                          .repeatForever(
                            u().to(1, { opacity: 255 }).to(1, { opacity: 170 })
                          )
                          .start(),
                        this.bbr.on(c.TOUCH_START, function () {
                          App.gameLoading.complete(function () {
                            dispatch(v.CLICK_GAME_LOADING_CONFIRM_BTN),
                              t.close();
                          });
                        }),
                        (this.startGame.getComponent(p).spriteFrame =
                          y.getDirSp(d[d.g1001], e, "l_font"));
                    }),
                    (a.setPageSpines = function () {
                      var t = this;
                      this.pageView.content.children.forEach(function (e, n) {
                        var i = e.getChildByName("intro");
                        if (i) {
                          var r = i.getComponent(f.Skeleton);
                          t.spineNodes.push(r), t.resetSpine(r, "p" + (n + 1));
                        }
                      });
                    }),
                    (a.onPageTurning = function () {
                      var t = this.pageView.getCurrentPageIndex();
                      this.playSpineAnim(t), this.setInfoTextSprite(t);
                    }),
                    (a.setInfoTextSprite = function (t) {
                      var e = T.getData().filePaths.localeSpriteFrame;
                      this.infoTextSprite.spriteFrame = y.getDirSp(
                        d[d.g1001],
                        e,
                        "intro_text_" + P.zeroPad(t + 1)
                      );
                    }),
                    (a.resetSpine = function (t, e) {
                      t.clearTracks(),
                        t.setToSetupPose(),
                        t.setAnimation(0, e, !1),
                        (t.paused = !0);
                    }),
                    (a.playSpineAnim = function (t) {
                      var e = this;
                      this.spineNodes.forEach(function (n, i) {
                        var r = "p" + (i + 1);
                        i === t
                          ? ((n.paused = !1),
                            n.clearTracks(),
                            n.setToSetupPose(),
                            n.setAnimation(0, r, !0))
                          : e.resetSpine(n, r);
                      });
                    }),
                    (a.onPrevPage = function () {
                      var t = this.pageView.getCurrentPageIndex(),
                        e = Math.max(0, t - 1);
                      this.pageView.scrollToPage(e, 0.3);
                    }),
                    (a.onNextPage = function () {
                      var t = this.pageView.getCurrentPageIndex(),
                        e = this.pageView.content.children.length - 1,
                        n = Math.min(e, t + 1);
                      this.pageView.scrollToPage(n, 0.3);
                    }),
                    (a.reset = function () {}),
                    (a.setData = function (t) {}),
                    (a.addEvents = function () {}),
                    o(e, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(A);
                        },
                      },
                    ]),
                    e
                  );
                })(b)).prototype,
                "pageView",
                [I],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (k = e(U.prototype, "bbr", [x], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (E = e(U.prototype, "startGame", [D], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (B = e(U.prototype, "gameLogo", [L], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (M = e(U.prototype, "leftArrow", [G], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (R = e(U.prototype, "rightArrow", [_], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (O = e(U.prototype, "infoTextSprite", [F], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (N = U))
            ) || N)
          );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/JackpotView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkEvent.ts",
    "./CmmSlotUtils.ts",
    "./MathUtil.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./ReplayModel.ts",
  ],
  function (t) {
    "use strict";
    var e,
      i,
      n,
      a,
      o,
      s,
      c,
      l,
      r,
      u,
      p,
      h,
      d,
      f,
      m,
      _,
      P,
      O,
      N,
      A,
      g,
      T,
      C,
      v,
      M;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (i = t.inheritsLoose),
            (n = t.initializerDefineProperty),
            (a = t.assertThisInitialized),
            (o = t.createClass);
        },
        function (t) {
          (s = t.cclegacy),
            (c = t._decorator),
            (l = t.sp),
            (r = t.NodeEventType),
            (u = t.Tween),
            (p = t.tween),
            (h = t.Vec3),
            (d = t.Node),
            (f = t.Label);
        },
        function (t) {
          m = t.default;
        },
        function (t) {
          _ = t.inject;
        },
        function (t) {
          P = t.default;
        },
        function (t) {
          O = t.SlotFrameworkEvent;
        },
        function (t) {
          N = t.CmmSlotUtils;
        },
        function (t) {
          A = t.default;
        },
        function (t) {
          (g = t.EBTM), (T = t.default);
        },
        function (t) {
          C = t.default;
        },
        function (t) {
          v = t.GameEvent;
        },
        function (t) {
          M = t.default;
        },
      ],
      execute: function () {
        var w, J, y, I, b, S, k, B, D, R, L, j, U;
        t("EJackpotType", void 0),
          s._RF.push({}, "200205pEgNEcIDHsp4qhx+3", "JackpotView", void 0);
        var E,
          F = c.ccclass;
        c.property;
        !(function (t) {
          (t.MINI = "jp-mini"),
            (t.MINOR = "jp-minor"),
            (t.MAJOR = "jp-major"),
            (t.GRAND = "jp-grand");
        })(E || (E = t("EJackpotType", {})));
        t(
          "JackpotView",
          ((w = F("JackpotView")),
          (J = _("alert", d)),
          (y = _("alert/effectBg", l.Skeleton)),
          (I = _("alert/effectFont", l.Skeleton)),
          (b = _("alert/totalWin", f)),
          (S = _("alert/coinSprays", d)),
          w(
            ((D = e(
              (B = (function (t) {
                function e() {
                  for (
                    var e, i = arguments.length, o = new Array(i), s = 0;
                    s < i;
                    s++
                  )
                    o[s] = arguments[s];
                  return (
                    (e = t.call.apply(t, [this].concat(o)) || this),
                    n(e, "alert", D, a(e)),
                    n(e, "effectBg", R, a(e)),
                    n(e, "effectFont", L, a(e)),
                    n(e, "totalWin", j, a(e)),
                    n(e, "coinSprays", U, a(e)),
                    (e.jackpotFileNames = [
                      "jp_mini",
                      "jp_minor",
                      "jp_major",
                      "jp_grand",
                    ]),
                    (e.jackpotTypes = [E.MINI, E.MINOR, E.MAJOR, E.GRAND]),
                    (e.jackpotNamesMap = new Map()),
                    (e.completedCB = null),
                    (e.tweenNumTween = null),
                    e
                  );
                }
                i(e, t);
                var s = e.prototype;
                return (
                  (s.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (s.start = function () {
                    this.init();
                  }),
                  (s.onDestroy = function () {
                    t.prototype.onDestroy.call(this);
                  }),
                  (s.init = function () {
                    for (var t = 0; t < this.jackpotFileNames.length; t++)
                      this.jackpotNamesMap.set(
                        this.jackpotTypes[t],
                        this.jackpotFileNames[t]
                      );
                    this.closeNodes();
                  }),
                  (s.showJp = function (t) {
                    var e = this,
                      i = this.data.getData().definition.digital,
                      n = this.data.getData().gameState,
                      a = n.totalWinnings,
                      o = n.isJp,
                      s = +N.formatJPNumber(a, !1, !1, i),
                      c = {
                        label: this.totalWin,
                        start: 0,
                        end: s,
                        tweenTime: 10,
                        digital: i,
                        useThousandsSeparator: !0,
                      };
                    (this.completedCB = function () {
                      t(), e.closeAlert();
                    }),
                      (this.alert.active = !0),
                      this.playAnimation(o, 10),
                      this.scheduleOnce(function () {
                        (e.totalWin.node.active = !0),
                          (e.tweenNumTween = N.tweenJPNum(c)),
                          e.alert.once(r.TOUCH_END, e.showJpResult, e),
                          dispatch(O.UPDATE_TOTAL_WINNINGS, {
                            data: { value: s, tweenTime: 10 },
                          }),
                          dispatch(v.UPDATE_WIN_AMOUNT, {
                            data: { value: s, tweenTime: 10 },
                          });
                      }, 2);
                  }),
                  (s.closeAlert = function () {
                    this.closeNodes(),
                      this.unscheduleAllCallbacks(),
                      u.stopAllByTarget(this.totalWin.node),
                      dispatch(v.STOP_BTM, { data: g.JP_POPUP_LOOP_1 }),
                      dispatch(v.STOP_BTM, { data: g.JP_POPUP_LOOP_2 }),
                      dispatch(v.STOP_BTM, { data: g.JP_POPUP_IN_1 }),
                      dispatch(v.STOP_BTM, { data: g.JP_POPUP_IN_2 }),
                      dispatch(v.STOP_BTM, { data: g.JP_MINI_VOCAL }),
                      dispatch(v.STOP_BTM, { data: g.JP_MINOR_VOCAL }),
                      dispatch(v.STOP_BTM, { data: g.JP_MAJOR_VOCAL }),
                      dispatch(v.STOP_BTM, { data: g.JP_GRAND_VOCAL }),
                      App.globalAudio.resumeMusic(),
                      this.alert.targetOff(r.TOUCH_END);
                  }),
                  (s.closeNodes = function () {
                    (this.alert.active = !1),
                      (this.effectBg.node.active = !1),
                      (this.effectFont.node.active = !1),
                      (this.totalWin.node.active = !1),
                      (this.coinSprays.active = !1),
                      this.coinSprays.children.forEach(function (t) {
                        t.active = !1;
                      }),
                      this.alert.targetOff(this),
                      T.stopOnJpPrize && (P.active = !1);
                  }),
                  (s.playAnimation = function (t, e) {
                    var i = this,
                      n = T.getData().bigwinAutoCloseTime,
                      a = this.jackpotNamesMap.get(t),
                      o = t == E.GRAND ? a + "_bg" : "jp_major_minor_mini_bg",
                      s =
                        t == E.MINI || t == E.MINOR
                          ? g.JP_POPUP_IN_1
                          : g.JP_POPUP_IN_2,
                      c =
                        t == E.MINI || t == E.MINOR
                          ? g.JP_POPUP_LOOP_1
                          : g.JP_POPUP_LOOP_2,
                      l = this.getJpVocal(t);
                    App.globalAudio.pauseMusic(),
                      (this.effectBg.node.active = !0),
                      (this.effectFont.node.active = !0),
                      (this.effectFont.skeletonData =
                        this.data.getGameAlertSpine(a)),
                      this.effectFont.setAnimation(0, "in", !1),
                      this.effectFont.setCompleteListener(function () {
                        i.effectFont.setAnimation(0, "loop", !0);
                      }),
                      (this.effectBg.skeletonData =
                        this.data.getGameAlertSpine(o)),
                      this.effectBg.setAnimation(0, "loop", !0),
                      dispatch(v.PLAY_BTM, { data: { url: l } }),
                      dispatch(v.PLAY_BTM, { data: { url: s } }),
                      this.scheduleOnce(function () {
                        i.showCoinSpray(),
                          dispatch(v.PLAY_BTM, { data: { url: c, loop: !0 } });
                      }, 2),
                      n && this.scheduleOnce(this.showJpResult, n + 2 + e),
                      this.scheduleOnce(this.addClickAlertCompleteCb, 2 + e);
                  }),
                  (s.playBounceTween = function (t, e) {
                    p(t)
                      .to(0.1, { scale: new h(1.8, 1.8, 1.8) })
                      .delay(0.01)
                      .to(
                        0.1,
                        { scale: new h(1, 1, 1) },
                        {
                          onComplete: function () {
                            e && e();
                          },
                        }
                      )
                      .start();
                  }),
                  (s.showCoinSpray = function () {
                    var t = this,
                      e = this.coinSprays.getComponentsInChildren(l.Skeleton);
                    this.coinSprays.active = !0;
                    for (
                      var i = function () {
                          var i = e[n];
                          0 == n
                            ? ((i.node.active = !0),
                              i.setAnimation(0, "coin_01", !1))
                            : 1 == n
                            ? t.scheduleOnce(function () {
                                (i.node.active = !0),
                                  i.setAnimation(0, "coin_02", !1);
                              }, 1.3)
                            : t.scheduleOnce(function () {
                                var t = A.getRandomNumber(3, 6);
                                (i.node.active = !0),
                                  i.setAnimation(0, "radom_0" + t, !1),
                                  i.setCompleteListener(function () {
                                    var t = A.getRandomNumber(3, 6);
                                    i.setAnimation(0, "radom_0" + t, !1);
                                  });
                              }, 2.8 + 0.5 * (n - 2));
                        },
                        n = 0;
                      n < e.length;
                      n++
                    )
                      i();
                  }),
                  (s.showJpResult = function () {
                    var t = this.data.getData().gameState.totalWinnings,
                      e = this.data.getData().definition.digital,
                      i = N.formatJPNumber(t, !0, !0, e),
                      n = +N.formatJPNumber(t, !1, !1, e);
                    this.unschedule(this.completedCB),
                      this.unschedule(this.showJpResult),
                      this.tweenNumTween && this.tweenNumTween.stop(),
                      (this.totalWin.string = i),
                      this.playBounceTween(this.totalWin.node),
                      this.addClickAlertCompleteCb(),
                      dispatch(v.QUICK_STOP_TOTAL_WINNINGS, { data: n }),
                      dispatch(v.QUICK_STOP_WIN_AMOUNT, { data: n });
                  }),
                  (s.addClickAlertCompleteCb = function () {
                    if (M.isReplay) {
                      var t = T.getData().bigwinAutoCloseTime;
                      this.scheduleOnce(this.completedCB, t),
                        this.alert.once(r.TOUCH_END, this.completedCB),
                        this.unschedule(this.addClickAlertCompleteCb);
                    } else
                      this.alert.once(r.TOUCH_END, this.completedCB),
                        this.unschedule(this.addClickAlertCompleteCb);
                  }),
                  (s.getJpVocal = function (t) {
                    switch (t) {
                      case E.MINI:
                        return g.JP_MINI_VOCAL;
                      case E.MINOR:
                        return g.JP_MINOR_VOCAL;
                      case E.MAJOR:
                        return g.JP_MAJOR_VOCAL;
                      case E.GRAND:
                        return g.JP_GRAND_VOCAL;
                    }
                  }),
                  (s.reset = function () {}),
                  (s.setData = function (t) {}),
                  (s.show = function () {
                    this.node.active = !0;
                  }),
                  (s.hide = function () {
                    this.node.active = !1;
                  }),
                  (s.addEvents = function () {
                    var t = this;
                    this.on(v.SHOW_JP, function (e) {
                      t.showJp(e.complete);
                    });
                  }),
                  o(e, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(C);
                      },
                    },
                  ]),
                  e
                );
              })(m)).prototype,
              "alert",
              [J],
              {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              }
            )),
            (R = e(B.prototype, "effectBg", [y], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (L = e(B.prototype, "effectFont", [I], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (j = e(B.prototype, "totalWin", [b], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (U = e(B.prototype, "coinSprays", [S], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (k = B))
          ) || k)
        );
        s._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/NewSpinClosedCmd.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./Flow.ts",
    "./SingletonExtends.ts",
    "./AutoPlayModel.ts",
    "./SlotFrameworkData.ts",
    "./SlotFrameworkEvent.ts",
    "./PlatformModel.ts",
    "./type2.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./FlowIDs.ts",
  ],
  function (t) {
    "use strict";
    var e, a, n, i, l, s, o, u, c, r, d, p, S, E, f;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose), (a = t.createClass);
        },
        function (t) {
          n = t.cclegacy;
        },
        function (t) {
          i = t.FlowTrigger;
        },
        function (t) {
          l = t.SingletonExtends;
        },
        function (t) {
          s = t.default;
        },
        function (t) {
          o = t.default;
        },
        function (t) {
          u = t.SlotFrameworkEvent;
        },
        function (t) {
          c = t.default;
        },
        function (t) {
          r = t.ESpinStatus;
        },
        function (t) {
          d = t.default;
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          S = t.GameEvent;
        },
        function (t) {
          E = t.EGameType;
        },
        function (t) {
          f = t.FlowIDs;
        },
      ],
      execute: function () {
        n._RF.push({}, "842849+OWlCJpbUtFn7tRWW", "NewSpinClosedCmd", void 0);
        t(
          "default",
          (function (t) {
            function n() {
              return t.apply(this, arguments) || this;
            }
            e(n, t);
            var l = n.prototype;
            return (
              (l.execute = function () {
                dispatch(S.SPIN_CLOSED), (d.quickStopCount = 0);
                var t = this.createFlow();
                App.flowManager.registerFlow(t);
              }),
              (l.createFlow = function () {
                var t = new App.flowManager.Flow(f.SPIN_CLOSED_FLOW),
                  e = this.data.getData().parser.newTimesSymbols,
                  a = d.getData(),
                  n = a.hasTimesSymbolsDelay,
                  l = a.nextSpinDelay,
                  o = e.length ? n : l,
                  p = this.data.currSpinData,
                  _ = p.currentView,
                  m = p.totalViews;
                return (
                  (this.data.getData().isResuming = !1),
                  this.calculateAutoSpin(),
                  _ === m - 1 && this.data.currentGameType === E.FREE_GAME
                    ? dispatch(u.UPDATE_SPIN_STATUS, { data: r.SPINING })
                    : dispatch(u.UPDATE_SPIN_STATUS, {
                        data: s.active ? r.SPINING : r.IDLE,
                      }),
                  t.add(
                    i.CONCURRENT,
                    new S(
                      u.UPDATE_USER_BALANCE,
                      { balance: c.amount },
                      { autoComplete: !0 }
                    )
                  ),
                  s.active && (s.spinsRemaining > 0 || -1 === s.spinsRemaining)
                    ? this.data.isOpenEarlyFlag
                      ? null == this.data.earlyData
                        ? t.add(
                            i.AFTER_PREVIOUS,
                            new S(S.WAIT_EARLY_SPIN_RESPONSE, null, {
                              autoComplete: !0,
                            })
                          )
                        : t.add(
                            i.AFTER_PREVIOUS,
                            new S(
                              S.CREATE_SPIN_FLOW,
                              { spinId: null, cheat: null, earlySpin: !0 },
                              { autoComplete: !0, delay: o }
                            )
                          )
                      : t.add(
                          i.AFTER_PREVIOUS,
                          new S(
                            S.CREATE_SPIN_FLOW,
                            { spinId: null, cheat: null },
                            { autoComplete: !0, delay: o }
                          )
                        )
                    : this.data.earlyData &&
                      this.data.isSendOutEarlyFlag &&
                      t.add(
                        i.AFTER_PREVIOUS,
                        new S(
                          S.CREATE_SPIN_FLOW,
                          { spinId: null, cheat: null, earlySpin: !0 },
                          { autoComplete: !0, delay: o }
                        )
                      ),
                  t
                );
              }),
              (l.calculateAutoSpin = function () {
                0 === s.spinsRemaining &&
                  ((s.active = !1), dispatch(u.SHOW_AUTO_SPIN, { data: !0 })),
                  s.spinsRemaining <= -1 && (s.spinsRemaining = -1),
                  s.active
                    ? dispatch(u.SHOW_AUTO_SPIN, { data: !1 })
                    : (dispatch(u.SHOW_AUTO_SPIN, { data: !0 }),
                      (s.spinsRemaining = 0));
              }),
              a(n, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(p);
                  },
                },
                {
                  key: "slotData",
                  get: function () {
                    return App.dataCenter.get(o);
                  },
                },
              ]),
              n
            );
          })(l).instance()
        );
        n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/ParseResponse.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./StakeModel.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./ReplayModel.ts",
    "./GameSender.ts",
    "./type2.ts",
    "./DefinitionModel.ts",
  ],
  function (e) {
    "use strict";
    var t, a, n, i, s, r, p, l, o, u, d, g;
    return {
      setters: [
        function (e) {
          t = e.createClass;
        },
        function (e) {
          a = e.cclegacy;
        },
        function (e) {
          n = e.default;
        },
        function (e) {
          i = e.default;
        },
        function (e) {
          s = e.default;
        },
        function (e) {
          r = e.GameEvent;
        },
        function (e) {
          p = e.EGameType;
        },
        function (e) {
          (l = e.default), (o = e.EReplayMode);
        },
        function (e) {
          u = e.GameSender;
        },
        function (e) {
          d = e.EDebugLogLevel;
        },
        function (e) {
          g = e.default;
        },
      ],
      execute: function () {
        a._RF.push({}, "8202bCWGH9EV5KQ35FrkQR6", "ParseResponse", void 0);
        e(
          "default",
          (function () {
            function e() {}
            return (
              (e.parseInit = function (e) {}),
              (e.parseNewInit = function (e) {
                var t;
                (this.data.currSpinIndex = 0),
                  this.data.setNewInitData(e),
                  n.init({
                    stakeList: e.platform.game.stakeValues,
                    stakeIndex: e.platform.player.settings.stakeIndex,
                    ratioList: e.platform.game.ratioValues,
                    ratioIndex: e.platform.player.settings.ratioIndex,
                    numWinlines: e.engine.definition.winlineDefs.length,
                    totalBetValues:
                      null == (t = e.platform) ? void 0 : t.game.stakeList,
                  }),
                  i.setNewData(e),
                  this.setNewGameType(),
                  dispatch(r.PARSER_INIT_COMPLETED);
              }),
              (e.parseSpin = function (e) {
                this.checkSpinErrorDebugLog(e),
                  this.setGameType(e),
                  dispatch(r.PARSER_SPIN_COMPLETED);
              }),
              (e.parseNewSpin = function (e) {
                this.data.setNewSpinData(e),
                  this.setNewGameType(),
                  this.data.judgeIsOpenEarlyFlag(),
                  dispatch(r.PARSER_SPIN_COMPLETED);
              }),
              (e.parseNewEarlySpin = function (e) {
                this.data.setNewSpinData(e),
                  this.setNewGameType(),
                  this.data.judgeIsOpenEarlyFlag();
              }),
              (e.parseEarlySpin = function (e) {
                this.data.earlyData = e;
              }),
              (e.tempEarlyClose = function (e) {
                this.data.earlyCloseData = e;
              }),
              (e.parseCloseSpin = function (e) {
                dispatch(r.PARSER_CLOSE_SPIN_COMPLETED);
              }),
              (e.parseReplay = function (e) {
                this.parseReplayData(e);
                var t = l.index;
                this.data.setReplayInit(e),
                  this.data.setReplayCurrentView(e.betData.theResult[t]),
                  l.replayMode !== o.RANKING_REPLAY &&
                    dispatch(r.PARSER_REPLAY_COMPLETED, !0);
              }),
              (e.parseReplayAgain = function (e) {
                this.parseReplayData(e);
                var t = l.index;
                this.data.setReplayCurrentView(e.betData.theResult[t]),
                  dispatch(r.PARSER_REPLAY_COMPLETED, !1);
              }),
              (e.parseReplayData = function (e) {
                var t = e.definition
                  ? e.definition.winlineDefs
                  : g.getData().winlineDefs;
                n.init({
                  stakeList: e.betData.replayMeta.stakeValues,
                  stakeIndex: e.betData.replayMeta.stakeIndex,
                  ratioList: e.betData.replayMeta.ratioValues,
                  ratioIndex: e.betData.replayMeta.ratioIndex,
                  numWinlines: t.length,
                });
                var a = e.betData.theResult[0].engine,
                  i = e.betData.theResult[1].engine;
                (a.currentView = 0),
                  (a.totalWinnings = 0),
                  (a.roundWinnings = 0),
                  (a.action = "spin"),
                  (a.isJp = ""),
                  (a.timesSymbols = []),
                  e.betData.theResult.forEach(function (t, n) {
                    n > 0 &&
                      ((t.engine.totalViews += 1),
                      (t.engine.currentView += 1),
                      (a.totalViews = i.totalViews),
                      (e.betData.totalViews = a.totalViews));
                  });
              }),
              (e.setGameType = function (e) {
                var t, a;
                "spin" ===
                (null == (t = e.engine.gameState) ? void 0 : t.action)
                  ? (a = p.MAIN_GAME)
                  : ((a = p.FREE_GAME),
                    this.data.previousGameType || (a = p.MAIN_GAME)),
                  (this.data.currentGameType = a);
              }),
              (e.setNewGameType = function () {
                var e,
                  t = this.data.currSpinData;
                "spin" === (null == t ? void 0 : t.action)
                  ? (e = p.MAIN_GAME)
                  : ((e = p.FREE_GAME),
                    this.data.previousGameType || (e = p.MAIN_GAME)),
                  (this.data.currentGameType = e);
              }),
              (e.checkSpinErrorDebugLog = function (e) {
                if (
                  e.engine.gameState.view &&
                  e.engine.gameState.view.length > 0
                ) {
                  if (null !== this.data.preData.gameState) {
                    var t =
                        this.data.getData().gameState.view.join() ===
                        e.engine.gameState.view.join(),
                      a = e.engine.gameState.spinId;
                    t &&
                      (Log.e("spin資料(view)重複"),
                      App.senderManager
                        .get(u)
                        .debugLog({
                          level: d.ERROR,
                          id: a,
                          message: "spin資料(view)重複",
                          data: {
                            resData: e.engine.gameState,
                            currentData: this.data.getData().gameState,
                            preData: this.data.preData.gameState,
                          },
                          tag: "repeatSpinData",
                        }));
                  }
                } else {
                  var n = e.engine.gameState.spinId;
                  App.senderManager
                    .get(u)
                    .debugLog({
                      level: d.ERROR,
                      id: n,
                      message: "沒有盤面資料",
                      data: e.engine.gameState,
                    });
                }
              }),
              t(e, null, [
                {
                  key: "data",
                  get: function () {
                    return App.dataCenter.get(s);
                  },
                },
              ]),
              e
            );
          })()
        );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/PrizeView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
  ],
  function (t) {
    "use strict";
    var e, i, n, o, r, c, s, a, u;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (i = t.inheritsLoose),
            (n = t.initializerDefineProperty),
            (o = t.assertThisInitialized);
        },
        function (t) {
          (r = t.cclegacy), (c = t._decorator), (s = t.Node);
        },
        function (t) {
          a = t.default;
        },
        function (t) {
          u = t.inject;
        },
      ],
      execute: function () {
        var l, f, p, d, h;
        r._RF.push({}, "1f86fbxtiRFgZeJqElxjkGQ", "PrizeView", void 0);
        var y = c.ccclass;
        c.property,
          t(
            "PrizeView",
            ((l = y("PrizeView")),
            (f = u("someNode", s)),
            l(
              ((h = e(
                (d = (function (t) {
                  function e() {
                    for (
                      var e, i = arguments.length, r = new Array(i), c = 0;
                      c < i;
                      c++
                    )
                      r[c] = arguments[c];
                    return (
                      (e = t.call.apply(t, [this].concat(r)) || this),
                      n(e, "someNode", h, o(e)),
                      e
                    );
                  }
                  i(e, t);
                  var r = e.prototype;
                  return (
                    (r.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (r.start = function () {
                      this.init();
                    }),
                    (r.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (r.init = function () {}),
                    (r.reset = function () {}),
                    (r.setData = function (t) {}),
                    (r.show = function () {
                      this.node.active = !0;
                    }),
                    (r.hide = function () {
                      this.node.active = !1;
                    }),
                    e
                  );
                })(a)).prototype,
                "someNode",
                [f],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (p = d))
            ) || p)
          );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/ReelView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./CmmSlotUtils.ts",
    "./MathUtil.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./PlatformModel.ts",
  ],
  function (t) {
    "use strict";
    var n, e, i, o, a, r, s, u, c, l, d, f, g, m, p, h, w, b, y, _, A, T, F, E;
    return {
      setters: [
        function (t) {
          (n = t.applyDecoratedDescriptor),
            (e = t.inheritsLoose),
            (i = t.initializerDefineProperty),
            (o = t.assertThisInitialized),
            (a = t.createClass);
        },
        function (t) {
          (r = t.cclegacy),
            (s = t._decorator),
            (u = t.sp),
            (c = t.tween),
            (l = t.Vec3),
            (d = t.macro),
            (f = t.Sprite),
            (g = t.Label),
            (m = t.Node),
            (p = t.UIOpacity);
        },
        function (t) {
          h = t.default;
        },
        function (t) {
          w = t.inject;
        },
        function (t) {
          b = t.CmmSlotUtils;
        },
        function (t) {
          y = t.default;
        },
        function (t) {
          (_ = t.default), (A = t.EBTM);
        },
        function (t) {
          T = t.default;
        },
        function (t) {
          F = t.GameEvent;
        },
        function (t) {
          E = t.default;
        },
      ],
      execute: function () {
        var I,
          v,
          N,
          B,
          S,
          W,
          R,
          C,
          D,
          M,
          G,
          O,
          L,
          P,
          z,
          U,
          x,
          k,
          q,
          V,
          H,
          j,
          Y,
          J,
          K,
          Q,
          X,
          Z;
        t("WIN_BOARD_ANIME_NAME", void 0),
          r._RF.push({}, "757ddeEppJHu7hyS1q9PSNz", "ReelView", void 0),
          (function (t) {
            (t.MG_IDLE = "mg_idle"),
              (t.FG_IDLE = "fg_idle"),
              (t.MG_WIN = "mg_win"),
              (t.FG_WIN = "fg_win");
          })(Z || (Z = t("WIN_BOARD_ANIME_NAME", {})));
        var $ = s.ccclass;
        s.property,
          t(
            "ReelView",
            ((I = $("ReelView")),
            (v = w("bgEffect", u.Skeleton)),
            (N = w("bgContent/bgLeft", f)),
            (B = w("bgContent/bgRight", f)),
            (S = w("winboard/bg", f)),
            (W = w("winboard/spine", u.Skeleton)),
            (R = w("winboard/winnings/winAmount", g)),
            (C = w("winboard/winnings/cross", g)),
            (D = w("winboard/winnings/times", g)),
            (M = w("fgRemaining", m)),
            (G = w("fgRemaining/remaining", g)),
            (O = w("winboard/fontNode/font", f)),
            (L = w("winboard/fontNode", p)),
            I(
              ((U = n(
                (z = (function (t) {
                  function n() {
                    for (
                      var n, e = arguments.length, a = new Array(e), r = 0;
                      r < e;
                      r++
                    )
                      a[r] = arguments[r];
                    return (
                      (n = t.call.apply(t, [this].concat(a)) || this),
                      i(n, "bgEffect", U, o(n)),
                      i(n, "bgLeft", x, o(n)),
                      i(n, "bgRight", k, o(n)),
                      i(n, "winboardBg", q, o(n)),
                      i(n, "spine", V, o(n)),
                      i(n, "winAmount", H, o(n)),
                      i(n, "cross", j, o(n)),
                      i(n, "times", Y, o(n)),
                      i(n, "fgRemaining", J, o(n)),
                      i(n, "remaining", K, o(n)),
                      i(n, "winBoardFont", Q, o(n)),
                      i(n, "fontNodeOpacity", X, o(n)),
                      (n.curWinBoardFontIndex = 0),
                      (n.curTimes = 0),
                      (n.fontNodeOpacityTween = null),
                      (n.winAmountTween = null),
                      (n.increaseCounts = 0),
                      (n.isMg = !0),
                      n
                    );
                  }
                  e(n, t);
                  var r = n.prototype;
                  return (
                    (r.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (r.start = function () {
                      this.init();
                    }),
                    (r.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (r.init = function () {
                      _.useProEffect || (this.bgEffect.node.active = !1),
                        (this.winAmount.node.active = !1),
                        (this.winBoardFont.node.parent.active = !0),
                        this.playWinBoardFontTween(!0);
                    }),
                    (r.setBgSprite = function (t) {
                      var n = t ? "mg_reel" : "fg_reel";
                      this.isMg = t;
                      var e = t ? "mg_winboard" : "fg_winboard",
                        i = this.data.getCommonSpriteFrame(n),
                        o = this.data.getCommonSpriteFrame(e);
                      (this.bgLeft.spriteFrame = this.bgRight.spriteFrame = i),
                        (this.winboardBg.spriteFrame = o);
                      var a = t ? Z.MG_IDLE : Z.FG_IDLE;
                      this.spine &&
                        (this.spine.clearTracks(),
                        this.spine.setToSetupPose(),
                        this.spine.setAnimation(0, a, !0));
                    }),
                    (r.setFgElements = function (t) {
                      var n = this.data.getData().gameState.freeGameCount;
                      (this.fgRemaining.active = !t),
                        (this.remaining.string =
                          null == n ? void 0 : n.toString()),
                        _.useProEffect && (this.bgEffect.node.active = !t);
                    }),
                    (r.updateWinAmount = function (t) {
                      var n = t.value,
                        e = t.tweenTime,
                        i = this.data.getData().definition.digital,
                        o = _.getData().winAmountTime,
                        a = {
                          label: this.winAmount,
                          start: parseFloat(
                            this.winAmount.string.replace(/,/g, "")
                          ),
                          end: n,
                          tweenTime: e || o,
                          digital: i,
                          useThousandsSeparator: !0,
                          callback: function () {},
                        };
                      n
                        ? ((this.winAmountTween = b.tweenNum(a)),
                          (this.winAmount.node.active = !0),
                          (this.winBoardFont.node.active = !1))
                        : ((this.winAmount.string = "0"),
                          (this.winAmount.node.active = !1),
                          (this.winBoardFont.node.active = !0));
                    }),
                    (r.quickStopWinAmount = function (t) {
                      this.winAmountTween && this.winAmountTween.stop(),
                        (this.winAmount.string = b.formatNumber(t));
                    }),
                    (r.updateFgRemaining = function () {
                      var t = this.data.getData().gameState.freeGameCount;
                      Number(this.remaining.string) != t &&
                        this.playBounceTween(this.remaining.node),
                        (this.remaining.string = t.toString());
                    }),
                    (r.IncreaseFgRemaining = function (t) {
                      var n = this,
                        e = this.data.getData().definition.extraFgRounds,
                        i = this.remaining.color;
                      this.increaseCounts++;
                      var o = 1 + 0.05 * this.increaseCounts,
                        a = 1 - 0.02 * this.increaseCounts;
                      c(this.remaining.node)
                        .to(
                          0.1,
                          { scale: new l(o, o, 1) },
                          {
                            onComplete: function () {
                              n.remaining.string = (
                                Number(n.remaining.string) + 1
                              ).toString();
                            },
                            easing: "quintIn",
                          }
                        )
                        .to(
                          0.05,
                          { scale: new l(a, a, 1) },
                          { easing: "quintIn" }
                        )
                        .call(function () {
                          n.increaseCounts == e
                            ? ((n.increaseCounts = 0),
                              n.scheduleOnce(function () {
                                t();
                              }, 1),
                              c(n.remaining.node)
                                .to(
                                  0.1,
                                  { scale: new l(1, 1, 1) },
                                  { easing: "quintIn" }
                                )
                                .start())
                            : n.increaseCounts < e && n.IncreaseFgRemaining(t);
                        })
                        .start(),
                        c(i)
                          .to(0.1, { a: 130 }, { easing: "quintIn" })
                          .to(0.05, { a: 255 }, { easing: "quintIn" })
                          .start();
                    }),
                    (r.playWinBoardAnime = function (t) {
                      var n = this,
                        e = t ? Z.MG_WIN : Z.FG_WIN;
                      this.spine &&
                        (this.spine.clearTracks(),
                        this.spine.setToSetupPose(),
                        this.spine.setAnimation(0, e, !1),
                        this.spine.setCompleteListener(function () {
                          var e = t ? Z.MG_IDLE : Z.FG_IDLE;
                          n.spine.setCompleteListener(function () {}),
                            n.spine.clearTracks(),
                            n.spine.setToSetupPose(),
                            n.spine.setAnimation(0, e, !0);
                        }));
                    }),
                    (r.playWinBoardFontTween = function (t) {
                      var n = this,
                        e = t ? [1, 2, 3, 4] : [5, 2, 3, 4];
                      this.unschedule(this.fontNodeOpacityTween),
                        (this.fontNodeOpacityTween = null),
                        (this.curWinBoardFontIndex = 0),
                        this.setWinBoardFont(e[this.curWinBoardFontIndex]),
                        (this.fontNodeOpacityTween = function () {
                          c(n.fontNodeOpacity)
                            .to(
                              1,
                              { opacity: 0 },
                              {
                                easing: "fade",
                                onComplete: function () {
                                  n.curWinBoardFontIndex == e.length - 1
                                    ? (n.curWinBoardFontIndex = 0)
                                    : n.curWinBoardFontIndex++,
                                    n.setWinBoardFont(
                                      e[n.curWinBoardFontIndex]
                                    );
                                },
                              }
                            )
                            .to(1, { opacity: 255 }, { easing: "fade" })
                            .start();
                        }),
                        this.schedule(
                          this.fontNodeOpacityTween,
                          5,
                          d.REPEAT_FOREVER,
                          3
                        );
                    }),
                    (r.setWinBoardFont = function (t) {
                      var n = "mg_font_winboard_0" + y.zeroPad(t, 1);
                      2 == t &&
                        E.getData().theme &&
                        "xin-star" == E.getData().theme &&
                        (n += "_01"),
                        (this.winBoardFont.spriteFrame =
                          this.data.getLocaleSpriteFrame(n));
                    }),
                    (r.expandWinnings = function () {
                      (this.times.string = ""),
                        (this.curTimes = 0),
                        this.times.color.set(255, 255, 255, 255),
                        this.cross.color.set(255, 255, 255, 255),
                        (this.cross.node.active = !0),
                        (this.times.node.active = !0);
                    }),
                    (r.mergeWinnings = function (t) {
                      var n = this,
                        e = this.data.getData().gameState,
                        i = e.totalWinnings,
                        o = e.roundWinnings,
                        a = "freeSpin" == e.action,
                        r = a ? o : i;
                      c(this.winAmount.node)
                        .delay(0.4)
                        .to(
                          0.4,
                          { position: new l(0, 3, 0) },
                          {
                            onComplete: function () {
                              (n.winAmount.string = b.formatNumber(r)),
                                n.playBounceTween(n.winAmount.node, t),
                                dispatch(F.PLAY_BTM, {
                                  data: { url: A.SCORE },
                                }),
                                a &&
                                  dispatch(F.UPDATE_FG_TOTAL_TIMES, {
                                    data: n.curTimes,
                                  });
                            },
                          }
                        )
                        .start(),
                        c(this)
                          .delay(0.75)
                          .call(function () {
                            n.playWinBoardAnime(n.isMg);
                          })
                          .start(),
                        c(this.times.node)
                          .delay(0.4)
                          .to(
                            0.4,
                            { position: new l(0, 17, 0) },
                            {
                              onStart: function () {
                                n.playFadeOut(n.times);
                              },
                            }
                          )
                          .start(),
                        c(this.cross.node)
                          .delay(0.4)
                          .to(
                            0.4,
                            { position: new l(0, 12, 0) },
                            {
                              onStart: function () {
                                n.playFadeOut(n.cross);
                              },
                            }
                          )
                          .start();
                    }),
                    (r.playBounceTween = function (t, n) {
                      c(t)
                        .to(0.1, { scale: new l(1.5, 1.5, 1.5) })
                        .delay(0.01)
                        .to(
                          0.1,
                          { scale: new l(1, 1, 1) },
                          {
                            onComplete: function () {
                              n && n();
                            },
                          }
                        )
                        .start();
                    }),
                    (r.playFadeOut = function (t) {
                      c(t.color)
                        .to(
                          0.4,
                          { a: 0 },
                          {
                            onComplete: function () {
                              t.node.active = !1;
                            },
                          }
                        )
                        .start();
                    }),
                    (r.updateTimes = function (t) {
                      (this.curTimes += t),
                        (this.times.string = this.curTimes.toString()),
                        this.times.forceDoLayout();
                    }),
                    (r.reset = function () {}),
                    (r.setData = function (t) {}),
                    (r.show = function () {
                      this.node.active = !0;
                    }),
                    (r.hide = function () {
                      this.node.active = !1;
                    }),
                    (r.addEvents = function () {
                      var t = this;
                      this.on(F.UPDATE_WIN_AMOUNT, function (n) {
                        t.updateWinAmount(n.data);
                      }),
                        this.on(F.QUICK_STOP_WIN_AMOUNT, function (n) {
                          t.quickStopWinAmount(n.data);
                        }),
                        this.on(F.CHANGE_GAME_STYLE, function (n) {
                          t.setBgSprite(n.data),
                            t.setFgElements(n.data),
                            t.playWinBoardFontTween(n.data);
                        }),
                        this.on(F.UPDATE_FG_REMAINING, function (n) {
                          t.updateFgRemaining();
                        }),
                        this.on(F.INCREASE_FG_REMAINING, function (n) {
                          t.IncreaseFgRemaining(n.complete);
                        }),
                        this.on(F.EXPAND_WIN_AMOUNT, function (n) {
                          t.expandWinnings();
                        }),
                        this.on(F.UPDATE_TIMES, function (n) {
                          t.playBounceTween(t.times.node),
                            t.updateTimes(n.data);
                        }),
                        this.on(F.MERGE_WIN_AMOUNT, function (n) {
                          t.mergeWinnings(n.data);
                        });
                    }),
                    a(n, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(T);
                        },
                      },
                    ]),
                    n
                  );
                })(h)).prototype,
                "bgEffect",
                [v],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (x = n(z.prototype, "bgLeft", [N], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (k = n(z.prototype, "bgRight", [B], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (q = n(z.prototype, "winboardBg", [S], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (V = n(z.prototype, "spine", [W], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (H = n(z.prototype, "winAmount", [R], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (j = n(z.prototype, "cross", [C], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (Y = n(z.prototype, "times", [D], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (J = n(z.prototype, "fgRemaining", [M], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (K = n(z.prototype, "remaining", [G], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (Q = n(z.prototype, "winBoardFont", [O], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (X = n(z.prototype, "fontNodeOpacity", [L], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (P = z))
            ) || P)
          );
        r._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/RegisterNewCommands.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./SingletonExtends.ts",
    "./GameEvent.ts",
    "./CreateReplayFlow.ts",
    "./CreateReplaySpinCompleteFlowCmd.ts",
    "./CreateReplayStopSpinFlowCmd.ts",
    "./CreateReplaySpinFlowCmd.ts",
    "./CreateReplayCloseSpinFlowCmd.ts",
    "./CreateReplayQuickStopFlowCmd.ts",
    "./CreateNewSpinFlowCmd.ts",
    "./CreateNewStopSpinFlowCmd.ts",
    "./CreateNewSpinCompleteFlowCmd.ts",
    "./NewSpinClosedCmd.ts",
    "./CreateNewCloseSpinFlowCmd.ts",
    "./CreateNewQuickStopFlowCmd.ts",
    "./CreateNewResumeFlowCmd.ts",
    "./CreateNewEarlySpinFlowCmd.ts",
  ],
  function (a) {
    "use strict";
    var e, n, t, d, o, m, C, p, u, c, l, i, r, E, _, s, f, S;
    return {
      setters: [
        function (a) {
          e = a.inheritsLoose;
        },
        function (a) {
          n = a.cclegacy;
        },
        function (a) {
          t = a.SingletonExtends;
        },
        function (a) {
          d = a.GameEvent;
        },
        function (a) {
          o = a.default;
        },
        function (a) {
          m = a.default;
        },
        function (a) {
          C = a.default;
        },
        function (a) {
          p = a.default;
        },
        function (a) {
          u = a.default;
        },
        function (a) {
          c = a.default;
        },
        function (a) {
          l = a.default;
        },
        function (a) {
          i = a.default;
        },
        function (a) {
          r = a.default;
        },
        function (a) {
          E = a.default;
        },
        function (a) {
          _ = a.default;
        },
        function (a) {
          s = a.default;
        },
        function (a) {
          f = a.default;
        },
        function (a) {
          S = a.default;
        },
      ],
      execute: function () {
        n._RF.push(
          {},
          "15ea3BISCdBrqzfShcdOAw1",
          "RegisterNewCommands",
          void 0
        );
        a(
          "default",
          (function (a) {
            function n() {
              return a.apply(this, arguments) || this;
            }
            return (
              e(n, a),
              (n.prototype.execute = function () {
                App.commandManager.addCommand(d.CREATE_SPIN_FLOW, l),
                  App.commandManager.addCommand(d.CREATE_STOP_SPIN_FLOW, i),
                  App.commandManager.addCommand(d.CREATE_SPIN_COMPLETE_FLOW, r),
                  App.commandManager.addCommand(d.CREATE_CLOSE_SPIN_FLOW, _),
                  App.commandManager.addCommand(d.SPIN_CLOSED_FLOW, E),
                  App.commandManager.addCommand(d.CREATE_RESUME_FLOW, f),
                  App.commandManager.addCommand(d.CREATE_QUICK_STOP_FLOW, s),
                  App.commandManager.addCommand(d.CREATE_EARLY_SPIN_FLOW, S),
                  App.commandManager.addCommand(d.CREATE_REPLAY_FLOW, o),
                  App.commandManager.addCommand(d.CREATE_REPLAY_SPIN_FLOW, p),
                  App.commandManager.addCommand(
                    d.CREATE_REPLAY_STOP_SPIN_FLOW,
                    C
                  ),
                  App.commandManager.addCommand(
                    d.CREATE_REPLAY_SPIN_COMPLETE_FLOW,
                    m
                  ),
                  App.commandManager.addCommand(
                    d.CREATE_REPLAY_CLOSE_SPIN_FLOW,
                    u
                  ),
                  App.commandManager.addCommand(
                    d.CREATE_REPLAY_QUICK_STOP_FLOW,
                    c
                  );
              }),
              n
            );
          })(t).instance()
        );
        n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/ReplayUIViewL.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./SlotFrameworkEvent.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./ReplayUIViewLBase.ts",
    "./ReplayUIViewBase.ts",
    "./ReplayModel.ts",
  ],
  function (t) {
    "use strict";
    var e, n, a, o, i, r, s, c, u, p, l, d, f;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose),
            (n = t.asyncToGenerator),
            (a = t.regeneratorRuntime),
            (o = t.createClass);
        },
        function (t) {
          (i = t.cclegacy), (r = t._decorator);
        },
        function (t) {
          s = t.SlotFrameworkEvent;
        },
        function (t) {
          (c = t.EInitName), (u = t.default);
        },
        function (t) {
          p = t.GameEvent;
        },
        function (t) {
          l = t.default;
        },
        function (t) {
          d = t.REPLAY_TYPE;
        },
        function (t) {
          f = t.default;
        },
      ],
      execute: function () {
        var _;
        i._RF.push({}, "9a6d3W4v9BC7qRNdK8pbxSw", "ReplayUIViewL", void 0);
        var h = r.ccclass;
        t(
          "default",
          h("ReplayUIViewL")(
            (_ = (function (t) {
              function i() {
                return t.apply(this, arguments) || this;
              }
              e(i, t);
              var r = i.prototype;
              return (
                (r.start = function () {
                  this.init(), this.switchShowContent(d.INFO_BAR);
                }),
                (r.onLoad = function () {
                  t.prototype.onLoad.call(this);
                }),
                (r.onDestroy = function () {
                  t.prototype.onDestroy.call(this);
                }),
                (r.boardAgainBtnHandler = function () {
                  this.switchShowContent(d.INFO_BAR),
                    dispatch(s.KILL_SYMBOLS),
                    (f.index = 0);
                  var t = f.getData();
                  dispatch(s.REPLAY_AGAIN, t);
                }),
                (r.quickStop = function () {
                  dispatch(p.REPLAY_START_QUICK_STOP);
                }),
                (r.addEvents = function () {
                  var e = this;
                  t.prototype.addEvents.call(this),
                    this.on(
                      s.REPLAY_BACK_TO_GAME,
                      n(
                        a().mark(function t(n) {
                          return a().wrap(function (t) {
                            for (;;)
                              switch ((t.prev = t.next)) {
                                case 0:
                                  e.data.restoreCurrentGameData(),
                                    dispatch(p.RESET_AND_OPEN_GAME_VIEW, {
                                      data: c.INIT_GAME,
                                    });
                                case 2:
                                case "end":
                                  return t.stop();
                              }
                          }, t);
                        })
                      )
                    ),
                    this.on(s.SHOW_REPLAY_END, function () {
                      dispatch(s.SHOW_REPLAY_BOARD_ALERT);
                    });
                }),
                o(i, [
                  {
                    key: "data",
                    get: function () {
                      return App.dataCenter.get(u);
                    },
                  },
                ]),
                i
              );
            })(l))
          ) || _
        );
        i._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/ReplayUIViewP.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./SlotFrameworkEvent.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./ReplayUIViewBase.ts",
    "./ReplayModel.ts",
    "./ReplayUIViewPBase.ts",
  ],
  function (t) {
    "use strict";
    var e, n, a, o, i, r, s, c, u, p, l, d, f;
    return {
      setters: [
        function (t) {
          (e = t.inheritsLoose),
            (n = t.asyncToGenerator),
            (a = t.regeneratorRuntime),
            (o = t.createClass);
        },
        function (t) {
          (i = t.cclegacy), (r = t._decorator);
        },
        function (t) {
          s = t.SlotFrameworkEvent;
        },
        function (t) {
          (c = t.EInitName), (u = t.default);
        },
        function (t) {
          p = t.GameEvent;
        },
        function (t) {
          l = t.REPLAY_TYPE;
        },
        function (t) {
          d = t.default;
        },
        function (t) {
          f = t.default;
        },
      ],
      execute: function () {
        var h;
        i._RF.push({}, "634d6zNdShABreibNrgaEyz", "ReplayUIViewP", void 0);
        var _ = r.ccclass;
        t(
          "default",
          _("ReplayUIViewP")(
            (h = (function (t) {
              function i() {
                return t.apply(this, arguments) || this;
              }
              e(i, t);
              var r = i.prototype;
              return (
                (r.start = function () {
                  this.init(), this.switchShowContent(l.INFO_BAR);
                }),
                (r.onLoad = function () {
                  t.prototype.onLoad.call(this);
                }),
                (r.onDestroy = function () {
                  t.prototype.onDestroy.call(this);
                }),
                (r.boardAgainBtnHandler = function () {
                  this.switchShowContent(l.INFO_BAR),
                    dispatch(s.KILL_SYMBOLS),
                    (d.index = 0);
                  var t = d.getData();
                  dispatch(s.REPLAY_AGAIN, t);
                }),
                (r.quickStop = function () {
                  dispatch(p.REPLAY_START_QUICK_STOP);
                }),
                (r.addEvents = function () {
                  var e = this;
                  t.prototype.addEvents.call(this),
                    this.on(
                      s.REPLAY_BACK_TO_GAME,
                      n(
                        a().mark(function t(n) {
                          return a().wrap(function (t) {
                            for (;;)
                              switch ((t.prev = t.next)) {
                                case 0:
                                  e.data.restoreCurrentGameData(),
                                    dispatch(p.RESET_AND_OPEN_GAME_VIEW, {
                                      data: c.INIT_GAME,
                                    });
                                case 2:
                                case "end":
                                  return t.stop();
                              }
                          }, t);
                        })
                      )
                    ),
                    this.on(s.SHOW_REPLAY_END, function () {
                      dispatch(s.SHOW_REPLAY_BOARD_ALERT);
                    });
                }),
                o(i, [
                  {
                    key: "data",
                    get: function () {
                      return App.dataCenter.get(u);
                    },
                  },
                ]),
                i
              );
            })(f))
          ) || h
        );
        i._RF.pop();
      },
    };
  }
);

System.register("chunks:///_virtual/res-type2.ts", ["cc"], function () {
  "use strict";
  var e;
  return {
    setters: [
      function (t) {
        e = t.cclegacy;
      },
    ],
    execute: function () {
      e._RF.push({}, "7b33cbueq9FdpGT0ebQKKEv", "res-type", void 0),
        e._RF.pop();
    },
  };
});

System.register("chunks:///_virtual/StaticData.ts", ["cc"], function (t) {
  "use strict";
  var e;
  return {
    setters: [
      function (t) {
        e = t.cclegacy;
      },
    ],
    execute: function () {
      t("slotTablePage2", void 0),
        e._RF.push({}, "e0634izrAxJrZYuldvx3PV4", "StaticData", void 0),
        e._RF.pop();
    },
  };
});

System.register("chunks:///_virtual/StaticFakeCmd.ts", ["cc"], function (t) {
  "use strict";
  var c;
  return {
    setters: [
      function (t) {
        c = t.cclegacy;
      },
    ],
    execute: function () {
      c._RF.push({}, "af178kUMmZLwrLOJblA7DWv", "StaticFakeCmd", void 0);
      t("default", function () {});
      c._RF.pop();
    },
  };
});

System.register(
  "chunks:///_virtual/Symbol.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameSymbolID.ts",
    "./GameEvent.ts",
    "./types.ts",
  ],
  function (t) {
    "use strict";
    var i, e, n, o, s, a, l, r, m, u, p, c, y, b, h, S, f, d, A, v, g, I, T;
    return {
      setters: [
        function (t) {
          (i = t.applyDecoratedDescriptor),
            (e = t.inheritsLoose),
            (n = t.initializerDefineProperty),
            (o = t.assertThisInitialized),
            (s = t.createClass);
        },
        function (t) {
          (a = t.cclegacy),
            (l = t._decorator),
            (r = t.sp),
            (m = t.Layers),
            (u = t.Tween),
            (p = t.tween),
            (c = t.UITransform),
            (y = t.Sprite),
            (b = t.Label);
        },
        function (t) {
          h = t.default;
        },
        function (t) {
          S = t.inject;
        },
        function (t) {
          (f = t.default), (d = t.EBTM);
        },
        function (t) {
          A = t.default;
        },
        function (t) {
          (v = t.EBackendSymbolID), (g = t.ESymbolAnimType);
        },
        function (t) {
          I = t.GameEvent;
        },
        function (t) {
          T = t.EPool;
        },
      ],
      execute: function () {
        var D, O, L, _, E, B, P, R, C, M, w, G, k, z, F, N, Y;
        a._RF.push({}, "7f3a9grRJlJrqcjTFQYeCFH", "Symbol", void 0);
        var x = l.ccclass;
        l.property,
          t(
            "Symbol",
            ((D = x("Symbol")),
            (O = S("frame", r.Skeleton)),
            (L = S("symbolSprite", y)),
            (_ = S("symbolSpriteBlur", y)),
            (E = S("upgrade", r.Skeleton)),
            (B = S("symbolOut", r.Skeleton)),
            (P = S("times", b)),
            (R = S("symbolAnimation", r.Skeleton)),
            D(
              ((w = i(
                (M = (function (t) {
                  function i() {
                    for (
                      var i, e = arguments.length, s = new Array(e), a = 0;
                      a < e;
                      a++
                    )
                      s[a] = arguments[a];
                    return (
                      (i = t.call.apply(t, [this].concat(s)) || this),
                      n(i, "frameSpine", w, o(i)),
                      n(i, "symbolSprite", G, o(i)),
                      n(i, "symbolSpriteBlur", k, o(i)),
                      n(i, "upgradeAnimation", z, o(i)),
                      n(i, "symbolOutSpine", F, o(i)),
                      n(i, "times", N, o(i)),
                      n(i, "symbolAnimation", Y, o(i)),
                      (i.symbolID = null),
                      (i.posId = null),
                      (i.isRare = null),
                      i
                    );
                  }
                  e(i, t);
                  var a = i.prototype;
                  return (
                    (a.onLoad = function () {}),
                    (a.start = function () {
                      this.node.layer = m.Enum.UI_2D;
                    }),
                    (a.onDestroy = function () {}),
                    (a.update = function (t) {}),
                    (a.setSymbolSprite = function (t) {
                      var i = this.isRare
                          ? t.toString().padStart(2, "0") + "_01"
                          : "" + t.toString().padStart(2, "0"),
                        e = this.data.getSymbolSpriteFrame(i);
                      (this.symbolSprite.spriteFrame = e),
                        (this.symbolSprite.node.active = !0);
                    }),
                    (a.setIsRare = function () {
                      var t = this,
                        i = this.data
                          .getData()
                          .gameState.timesSymbols.find(function (i) {
                            return i.isRare && i.symbolPos == t.posId;
                          });
                      this.isRare = !!i;
                    }),
                    (a.setTimesText = function (t) {
                      (this.times.node.active = !0),
                        (this.times.string = t ? t + "x" : "");
                    }),
                    (a.reset = function () {
                      (this.isRare = !1),
                        (this.symbolAnimation.node.active = !1),
                        (this.frameSpine.node.active = !1),
                        (this.symbolOutSpine.node.active = !1),
                        (this.symbolSpriteBlur.node.active = !1),
                        (this.symbolSprite.node.active = !0),
                        u.stopAllByTarget(this),
                        this.symbolAnimation &&
                          this.symbolAnimation.setCompleteListener(null),
                        this.symbolOutSpine &&
                          this.symbolOutSpine.setCompleteListener(null);
                    }),
                    (a.setData = function (t) {
                      var i = t.symbolId,
                        e = t.posId,
                        n = [
                          v.ORANGE_GEM,
                          v.RED_GEM,
                          v.PURPLE_GEM,
                          v.BLUE_GEM,
                          v.GREEN_GEM,
                        ].includes(i)
                          ? 1.15
                          : 1;
                      this.symbolSprite.node.setScale(n, n),
                        this.symbolAnimation.node.setScale(n, n),
                        this.symbolSpriteBlur.node.setScale(n, n),
                        (this.name = "" + e),
                        (this.posId = e),
                        (this.symbolID = i),
                        this.setIsRare(),
                        this.setSymbolSprite(i),
                        this.setSymbolBlur(i),
                        (this.times.node.active = !1);
                    }),
                    (a.recycleSymbol = function () {
                      this.hide(),
                        this.reset(),
                        App.pool.getPool(T.SYMBOL_POOL).put(this.node);
                    }),
                    (a.playLoopAnim = function () {
                      var t = this;
                      f.useProEffect &&
                        this.scheduleOnce(function () {
                          t.playAnim(t.symbolID, g.LOOP, !0);
                        }, 0);
                    }),
                    (a.playWinAnim = function (t) {
                      this.playAnim(this.symbolID, g.WIN, !1),
                        this.scheduleOnce(function () {
                          t && t();
                        }, 1),
                        (this.frameSpine.node.active = !0),
                        this.frameSpine.setAnimation(0, "win", !0);
                    }),
                    (a.playScatterInAnim = function () {
                      var t = this;
                      this.playAnim(this.symbolID, g.IN, !1, function () {
                        t.playAnim(t.symbolID, g.LOOP, !0);
                      }),
                        dispatch(I.PLAY_BTM, { data: { url: d.SCATTER_IN } });
                    }),
                    (a.playScatterInBtm = function () {
                      dispatch(I.PLAY_BTM, { data: { url: d.SCATTER_IN } });
                    }),
                    (a.playScatterInBtmFast = function () {
                      dispatch(I.PLAY_BTM, { data: { url: d.SCATTER_IN_X2 } });
                    }),
                    (a.playJackpotInAnim = function () {
                      var t = this;
                      this.playAnim(this.symbolID, g.IN, !1, function () {
                        t.playAnim(t.symbolID, g.LOOP, !0);
                      });
                    }),
                    (a.playScatterWinAnim = function (t) {
                      var i = this;
                      this.playAnim(this.symbolID, g.WIN, !1, function () {
                        i.playAnim(i.symbolID, g.LOOP, !0), t && t();
                      });
                    }),
                    (a.playJpWinAnim = function (t) {
                      var i = this;
                      this.playAnim(this.symbolID, g.WIN, !1, function () {
                        i.playAnim(i.symbolID, g.LOOP, !0), t && t();
                      });
                    }),
                    (a.playOutAnim = function () {
                      var t = this;
                      p(this)
                        .delay(0.13)
                        .call(function () {
                          (t.symbolAnimation.node.active = !1),
                            (t.symbolSprite.node.active = !1),
                            (t.frameSpine.node.active = !1),
                            t.symbolAnimation.setCompleteListener(null),
                            t.symbolOutSpine.setCompleteListener(null),
                            (t.symbolOutSpine.node.active = !0),
                            t.symbolOutSpine.setAnimation(0, "out", !1),
                            t.symbolOutSpine.setCompleteListener(function () {
                              t.recycleSymbol();
                            });
                        })
                        .start();
                    }),
                    (a.initTimesSymbol = function (t) {
                      var i = this.data.getData().gameState.timesSymbols;
                      if (i.length) {
                        var e = i.find(function (i) {
                            return i.symbolPos == t;
                          }),
                          n = e.symbol,
                          o = e.times;
                        this.setSymbolSprite(n), this.setTimesText(o);
                      }
                    }),
                    (a.openTimesSymbol = function (t) {
                      var i = this.data.getData().parser.newTimesSymbols;
                      if (i.length) {
                        var e = i.find(function (i) {
                            return i.symbolPos == t;
                          }),
                          n = e.symbol,
                          o = e.times;
                        this.setSymbolSprite(n), this.setTimesText(o);
                      }
                    }),
                    (a.playTimesSymbolsUpgrade = function (t) {
                      var i = this,
                        e = t.afterSymbol,
                        n = t.afterTimes;
                      (this.symbolID = e),
                        (this.upgradeAnimation.node.active = !0),
                        this.upgradeAnimation.setAnimation(0, "transition", !1),
                        this.upgradeAnimation.setCompleteListener(function () {
                          i.upgradeAnimation.node.active = !1;
                        }),
                        this.scheduleOnce(function () {
                          i.setTimesText(n);
                        }, 0.5),
                        dispatch(I.PLAY_BTM, {
                          data: { url: d.TIMES_SYMBOL_UPGRADE },
                        });
                    }),
                    (a.closeTimesLabel = function () {
                      this.times.node.active = !1;
                    }),
                    (a.playTimesSymbolsFunction = function () {
                      var t = this.isRare
                        ? this.symbolID.toString().padStart(2, "0") + "_01"
                        : "" + this.symbolID.toString().padStart(2, "0");
                      (this.symbolSprite.node.active = !1),
                        (this.symbolAnimation.node.active = !0),
                        (this.symbolAnimation.skeletonData =
                          this.data.getSymbolAnimSpine(t)),
                        this.symbolAnimation.setAnimation(0, "function", !1);
                    }),
                    (a.setSymbolBlur = function (t) {
                      var i = this.isRare
                          ? t.toString().padStart(2, "0") + "_01_blur"
                          : t.toString().padStart(2, "0") + "_blur",
                        e = this.data.getSymbolSpriteFrameBlur(i),
                        n = this.symbolSprite.node.getComponent(c),
                        o = n.width,
                        s = n.height;
                      this.symbolSpriteBlur
                        .getComponent(c)
                        .setContentSize(o, s),
                        (this.symbolSpriteBlur.spriteFrame = e);
                    }),
                    (a.setSymbolBlurActive = function (t) {}),
                    (a.playAnim = function (t, i, e, n) {
                      var o = this.isRare
                        ? t.toString().padStart(2, "0") + "_01"
                        : "" + t.toString().padStart(2, "0");
                      (this.symbolAnimation.node.active = !0),
                        (this.symbolSprite.node.active = !1),
                        (this.symbolAnimation.skeletonData =
                          this.data.getSymbolAnimSpine(o)),
                        this.symbolAnimation.setAnimation(0, i, e),
                        this.symbolAnimation.setCompleteListener(function (t) {
                          n && !t.loop && n();
                        });
                    }),
                    (a.show = function () {
                      this.node.active = !0;
                    }),
                    (a.hide = function () {
                      this.node.active = !1;
                    }),
                    s(i, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(A);
                        },
                      },
                    ]),
                    i
                  );
                })(h)).prototype,
                "frameSpine",
                [O],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (G = i(M.prototype, "symbolSprite", [L], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (k = i(M.prototype, "symbolSpriteBlur", [_], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (z = i(M.prototype, "upgradeAnimation", [E], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (F = i(M.prototype, "symbolOutSpine", [B], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (N = i(M.prototype, "times", [P], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (Y = i(M.prototype, "symbolAnimation", [R], {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              })),
              (C = M))
            ) || C)
          );
        a._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/SymbolView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Symbol.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameSymbolID.ts",
    "./GameEvent.ts",
    "./types.ts",
    "./SlotFrameworkEvent.ts",
  ],
  function (t) {
    "use strict";
    var o, e, n, s, i, a, l, r, c, S, m, u, y, h, p, f, b, d, O;
    return {
      setters: [
        function (t) {
          (o = t.inheritsLoose), (e = t.createClass);
        },
        function (t) {
          (n = t.cclegacy),
            (s = t._decorator),
            (i = t.instantiate),
            (a = t.bezierByTime),
            (l = t.tween),
            (r = t.Tween),
            (c = t.UITransform),
            (S = t.Vec3);
        },
        function (t) {
          m = t.default;
        },
        function (t) {
          u = t.Symbol;
        },
        function (t) {
          (y = t.default), (h = t.EBTM);
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          f = t.EBackendSymbolID;
        },
        function (t) {
          b = t.GameEvent;
        },
        function (t) {
          d = t.EPool;
        },
        function (t) {
          O = t.SlotFrameworkEvent;
        },
      ],
      execute: function () {
        var M;
        n._RF.push({}, "69b85XIVD9ID7fZRO0AFeBW", "SymbolView", void 0);
        var T = s.ccclass;
        s.property,
          t(
            "SymbolView",
            T("SymbolView")(
              (M = (function (t) {
                function n() {
                  for (
                    var o, e = arguments.length, n = new Array(e), s = 0;
                    s < e;
                    s++
                  )
                    n[s] = arguments[s];
                  return (
                    ((o =
                      t.call.apply(t, [this].concat(n)) || this).symbolsMap =
                      new Map()),
                    (o.oldSymbolsMap = new Map()),
                    (o.SYMBOL_ROW = 6),
                    (o.SYMBOL_COL = 5),
                    (o.TOTAL_SYMBOL = o.SYMBOL_ROW * o.SYMBOL_COL),
                    (o.GAME_HEIGHT = 720),
                    (o.BIG_SYMBOLS = [
                      f.EYE,
                      f.SNAKE,
                      f.BOW,
                      f.MACHETE,
                      f.SCATTER,
                      f.JACKPOT,
                    ]),
                    (o.TIMES_SYMBOLS = [f.T1, f.T2, f.T3, f.T4]),
                    (o.symbolOutTag = 1234),
                    (o.symbolInTag = 5678),
                    (o.isOutCompleted = !1),
                    (o.isStartSymbolIn = !1),
                    (o.needInitHeight = !1),
                    (o.fireballPosIds = []),
                    o
                  );
                }
                o(n, t);
                var s = n.prototype;
                return (
                  (s.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (s.start = function () {
                    this.createSymbolPool();
                  }),
                  (s.onDestroy = function () {
                    t.prototype.onDestroy.call(this);
                  }),
                  (s.createSymbolPool = function () {
                    for (
                      var t = y.getData().filePaths.symbolPrefab,
                        o = App.cache.get(this.data.module, t).data,
                        e = 0;
                      e < 2 * this.TOTAL_SYMBOL;
                      e++
                    ) {
                      var n = i(o);
                      n.addComponent(u),
                        (App.pool.createPool(d.SYMBOL_POOL).cloneNode = n),
                        App.pool.createPool(d.SYMBOL_POOL).put(n);
                    }
                  }),
                  (s.createSymbols = function (t) {
                    var o = this;
                    this.data.getData().parser.view1D.forEach(function (e, n) {
                      o.createSymbol(n, e, t);
                    }),
                      this.setSymbolsSiblingIndex();
                  }),
                  (s.createSymbol = function (t, o, e) {
                    var n = this.data.getData().symbolPosConfig,
                      s = App.pool.getPool(d.SYMBOL_POOL).get(),
                      i = s.getComponent(u),
                      a = this.BIG_SYMBOLS.includes(o),
                      l = this.TIMES_SYMBOLS.includes(o);
                    s.position.set(n.get(t)),
                      (s.name = "" + t),
                      e && (s.active = !0);
                    var r = { posId: t, symbolId: o };
                    this.symbolsMap.set(t, i),
                      this.node.addChild(s),
                      i.setData(r),
                      l && e && i.initTimesSymbol(t),
                      a && i.playLoopAnim();
                  }),
                  (s.setSymbolsSiblingIndex = function () {
                    for (var t = 0, o = 0; o < this.TOTAL_SYMBOL; o++) {
                      var e = this.symbolsMap.get(o);
                      this.TIMES_SYMBOLS.includes(e.symbolID)
                        ? (e.node.setSiblingIndex(29 - t), t++)
                        : e.node.setSiblingIndex(o);
                    }
                  }),
                  (s.showSymbolsOut = function (t) {
                    var o = this,
                      e = y.isTurbo,
                      n = this.configModel.reelConfig,
                      s = n.animStagger,
                      i = n.speed,
                      a = Array.from(this.oldSymbolsMap).sort(function (t, o) {
                        return t[0] - o[0];
                      }),
                      r = e
                        ? h.SYMBOL_TURBO_FALL_OUT
                        : h.SYMBOL_NORMAL_FALL_OUT,
                      c = 0,
                      m = 0;
                    this.isOutCompleted = !1;
                    for (var u = 0; u < this.SYMBOL_ROW; u++)
                      for (
                        var p = function () {
                            var e = a[f][1];
                            c++,
                              l(e.node)
                                .delay(c * s)
                                .by(
                                  i,
                                  { position: new S(0, -o.GAME_HEIGHT, 0) },
                                  {
                                    easing: "cubicInOut",
                                    onStart: function () {
                                      e.setSymbolBlurActive(!0);
                                    },
                                  }
                                )
                                .call(function () {
                                  m++,
                                    e.recycleSymbol(),
                                    m == o.TOTAL_SYMBOL &&
                                      ((o.isOutCompleted = !0), t());
                                })
                                .tag(o.symbolOutTag)
                                .start();
                          },
                          f = this.TOTAL_SYMBOL - this.SYMBOL_ROW + u;
                        f >= 0;
                        f -= this.SYMBOL_ROW
                      )
                        p();
                    dispatch(b.PLAY_BTM, { data: { url: r } });
                  }),
                  (s.showSymbolsIn = function (t) {
                    y.isTurbo
                      ? this.showTurboSymbolsIn(t)
                      : this.showNormalSymbolsIn(t);
                  }),
                  (s.showNormalSymbolsIn = function (t) {
                    for (
                      var o = this,
                        e = this.configModel.reelConfig,
                        n = e.animStagger,
                        s = e.speed,
                        i = Array.from(this.symbolsMap).sort(function (t, o) {
                          return t[0] - o[0];
                        }),
                        a = h.SYMBOL_NORMAL_FALL_IN,
                        r = 0,
                        c = 0,
                        m = 0;
                      m < this.SYMBOL_ROW;
                      m++
                    )
                      for (
                        var u = function () {
                            var e = i[p][1],
                              m = e.node.position,
                              u = m.x,
                              h = m.y,
                              d = m.z,
                              O = o.TIMES_SYMBOLS.includes(e.symbolID);
                            r++,
                              l(e.node)
                                .set({
                                  position: new S(u, h + o.GAME_HEIGHT, d),
                                  active: !0,
                                })
                                .delay(r * n)
                                .to(
                                  s,
                                  { position: new S(u, h, d) },
                                  {
                                    onStart: function () {
                                      O &&
                                        (dispatch(b.SHOW_FIRE_BALL, {
                                          data: e.posId,
                                        }),
                                        o.fireballPosIds.push(e.posId)),
                                        e.setSymbolBlurActive(!0);
                                    },
                                  }
                                )
                                .to(0.085, { position: new S(u, h - 20, d) })
                                .to(0.1, { position: new S(u, h, d) })
                                .call(function () {
                                  ++c == o.TOTAL_SYMBOL &&
                                    ((y.canQuickStop = !1),
                                    (o.fireballPosIds.length = 0),
                                    (o.isStartSymbolIn = !1),
                                    t()),
                                    1 == c &&
                                      dispatch(b.PLAY_BTM, {
                                        data: { url: a },
                                      }),
                                    e.symbolID == f.SCATTER &&
                                      e.playScatterInBtm(),
                                    O && o.openTimesSymbol(e.posId),
                                    e.setSymbolBlurActive(!1);
                                })
                                .tag(o.symbolInTag)
                                .start();
                          },
                          p = this.TOTAL_SYMBOL - this.SYMBOL_ROW + m;
                        p >= 0;
                        p -= this.SYMBOL_ROW
                      )
                        u();
                  }),
                  (s.showTurboSymbolsIn = function (t) {
                    for (
                      var o = this,
                        e = this.configModel.reelConfig.speed,
                        n = Array.from(this.symbolsMap).sort(function (t, o) {
                          return t[0] - o[0];
                        }),
                        s = h.SYMBOL_TURBO_FALL_IN,
                        i = 0,
                        a = 0;
                      a < this.SYMBOL_ROW;
                      a++
                    )
                      for (
                        var r = function () {
                            var a = n[m][1],
                              r = a.node.position,
                              u = r.x,
                              h = r.y,
                              p = r.z,
                              d = o.TIMES_SYMBOLS.includes(a.symbolID);
                            a.symbolID == f.SCATTER &&
                              (y.isTurbo
                                ? a.playScatterInBtmFast()
                                : a.playScatterInBtm());
                            var O = a.node.getComponent(c).height / 12,
                              M = Math.floor(m / 6),
                              T =
                                h + o.GAME_HEIGHT - 25 * (4 - M) - 60 * (4 - M);
                            l(a.node)
                              .set({ position: new S(u, T, p), active: !0 })
                              .to(
                                1.1 * e,
                                { position: new S(u, h - O, p) },
                                {
                                  easing: "quintOut",
                                  onStart: function () {
                                    d &&
                                      (dispatch(b.SHOW_FIRE_BALL, {
                                        data: a.posId,
                                      }),
                                      o.fireballPosIds.push(a.posId)),
                                      a.setSymbolBlurActive(!0);
                                  },
                                  onComplete: function () {
                                    l(a.node)
                                      .to(
                                        0.04,
                                        { position: new S(u, h, p) },
                                        {
                                          easing: "quadOut",
                                          onComplete: function () {
                                            ++i == o.TOTAL_SYMBOL &&
                                              ((y.canQuickStop = !1),
                                              (o.isStartSymbolIn = !1),
                                              (o.fireballPosIds.length = 0),
                                              t()),
                                              1 == i &&
                                                dispatch(b.PLAY_BTM, {
                                                  data: { url: s },
                                                }),
                                              d && o.openTimesSymbol(a.posId),
                                              a.setSymbolBlurActive(!1);
                                          },
                                        }
                                      )
                                      .start();
                                  },
                                }
                              )
                              .tag(o.symbolInTag)
                              .start();
                          },
                          m = this.TOTAL_SYMBOL - this.SYMBOL_ROW + a;
                        m >= 0;
                        m -= this.SYMBOL_ROW
                      )
                        r();
                  }),
                  (s.showSymbolsQuickIn = function (t) {
                    for (
                      var o = this,
                        e = this.data.getData().symbolPosConfig,
                        n = y.getData().symbolQuickInTime,
                        s = Array.from(this.symbolsMap).sort(function (t, o) {
                          return t[0] - o[0];
                        }),
                        i = 0,
                        a = 0;
                      a < this.SYMBOL_ROW;
                      a++
                    )
                      for (
                        var r = function () {
                            var a = s[c][1],
                              r = e.get(c),
                              m = o.TIMES_SYMBOLS.includes(a.symbolID),
                              u = o.needInitHeight
                                ? {
                                    position: new S(r.x, r.y + 300, r.z),
                                    active: !0,
                                  }
                                : { active: !0 };
                            a.symbolID == f.SCATTER && a.playScatterInBtmFast(),
                              l(a.node)
                                .set(u)
                                .to(
                                  n,
                                  { position: r },
                                  {
                                    easing: function (t) {
                                      return o.symbolsBezierByTime(t);
                                    },
                                    onStart: function () {
                                      m &&
                                        !o.fireballPosIds.includes(a.posId) &&
                                        dispatch(b.SHOW_FIRE_BALL_QUICK_STOP, {
                                          data: a.posId,
                                        }),
                                        a.setSymbolBlurActive(!0);
                                    },
                                    onComplete: function () {
                                      ++i == o.TOTAL_SYMBOL &&
                                        ((y.canQuickStop = !1),
                                        (o.isStartSymbolIn = !1),
                                        (o.needInitHeight = !1),
                                        (o.fireballPosIds.length = 0),
                                        t()),
                                        m && o.openTimesSymbol(a.posId),
                                        a.setSymbolBlurActive(!1);
                                    },
                                  }
                                )
                                .start();
                          },
                          c = this.TOTAL_SYMBOL - this.SYMBOL_ROW + a;
                        c >= 0;
                        c -= this.SYMBOL_ROW
                      )
                        r();
                  }),
                  (s.showCurrentViewFall = function (t) {
                    var o = this.data.getData().gameState.posTransform;
                    o.length || (t && t());
                    for (var e = 0; e < o.length; e++) {
                      var n = o[e],
                        s = n.beforePos,
                        i = n.afterPos,
                        a = e == o.length - 1 ? t : null;
                      this.updateSymbolMapIndex(s, i);
                      var l = this.symbolsMap.get(i);
                      (l.node.name = "" + i), this.moveTo(l.node, i, !1, e, a);
                    }
                  }),
                  (s.symbolsBezierByTimeTurbo = function (t) {
                    return a([0.73, 0.73, 0.66, 1.16], t);
                  }),
                  (s.symbolsBezierByTime = function (t) {
                    return a([0.67, 1.33, 0.61, 1], t);
                  }),
                  (s.playSymbolsWin = function (t) {
                    for (
                      var o = this.data.getData().gameState.winSymbols, e = 0;
                      e < o.length;
                      e++
                    )
                      for (var n = o[e].symbolPos, s = 0; s < n.length; s++) {
                        var i = n[s],
                          a =
                            n.length == s + 1 && o.length == e + 1
                              ? function () {
                                  t(),
                                    dispatch(b.STOP_BTM, {
                                      data: h.SYMBOL_WIN,
                                    });
                                }
                              : null;
                        this.symbolsMap.get(i).playWinAnim(a);
                      }
                    dispatch(b.PLAY_BTM, { data: { url: h.SYMBOL_WIN } });
                  }),
                  (s.playOutAnimAndRemoveSymbols = function (t) {
                    var o = this;
                    this.data
                      .getData()
                      .gameState.winSymbols.forEach(function (t) {
                        t.symbolPos.forEach(function (t) {
                          o.symbolsMap.get(t).playOutAnim(),
                            o.symbolsMap.delete(t);
                        });
                      }),
                      dispatch(b.PLAY_BTM, { data: { url: h.SYMBOL_BREAK } }),
                      l(this)
                        .delay(0.15)
                        .call(function () {
                          t();
                        })
                        .start();
                  }),
                  (s.killSymbols = function () {
                    this.symbolsMap.forEach(function (t) {
                      t.recycleSymbol();
                    }),
                      this.symbolsMap.clear(),
                      r.stopAll();
                  }),
                  (s.playScatterWin = function (t) {
                    var o = this,
                      e = this.data.getData().parser,
                      n = e.view1D.filter(function (t) {
                        return t == f.SCATTER;
                      }),
                      s = 0;
                    e.view1D.forEach(function (e, i) {
                      if (e == f.SCATTER) {
                        var a =
                          ++s == n.length
                            ? function () {
                                t(),
                                  dispatch(b.MUSIC_VOLUME_MULTIPLE, {
                                    data: 2,
                                  });
                              }
                            : null;
                        o.symbolsMap.get(i).playScatterWinAnim(a);
                      }
                    }),
                      dispatch(b.MUSIC_VOLUME_MULTIPLE, { data: 0.5 }),
                      dispatch(b.PLAY_BTM, { data: { url: h.SCATTER_WIN } });
                  }),
                  (s.playJpWin = function (t) {
                    var o = this,
                      e = this.data.getData().parser,
                      n = e.view1D.filter(function (t) {
                        return t == f.JACKPOT;
                      }),
                      s = 0;
                    e.view1D.forEach(function (e, i) {
                      if (e == f.JACKPOT) {
                        var a = ++s == n.length ? t : null;
                        o.symbolsMap.get(i).playJpWinAnim(a);
                      }
                    }),
                      dispatch(b.PLAY_BTM, { data: { url: h.JACKPOT_WIN } });
                  }),
                  (s.playRareUpgrade = function () {
                    for (
                      var t = this,
                        o = this.data.getData().gameState,
                        e = o.timesUpgrade,
                        n = o.posTransform,
                        s = function () {
                          var o = e[i],
                            s = null;
                          n.forEach(function (t) {
                            t.beforePos == o.symbolPos && (s = t.afterPos);
                          }),
                            s || (s = o.symbolPos),
                            t.symbolsMap.get(s).playTimesSymbolsUpgrade(o),
                            t.symbolsMap.get(s).playTimesSymbolsFunction();
                        },
                        i = 0;
                      i < e.length;
                      i++
                    )
                      s();
                  }),
                  (s.updateSymbolMapIndex = function (t, o) {
                    var e = this.symbolsMap.get(t);
                    this.symbolsMap.set(o, e), this.symbolsMap.delete(t);
                  }),
                  (s.moveTo = function (t, o, e, n, s) {
                    var i = this,
                      a = this.configModel.reelConfig,
                      r = a.speed,
                      m = a.animStagger,
                      y = this.data.getData().symbolPosConfig.get(o),
                      h = y.x,
                      p = y.y,
                      f = y.z,
                      d = t.getComponent(u),
                      O = this.TIMES_SYMBOLS.includes(d.symbolID),
                      M = d.node.getComponent(c).height / 12;
                    return l(t)
                      .delay(n * m)
                      .to(
                        0.6 * r,
                        { position: new S(h, p - M, f) },
                        {
                          easing: "quadOut",
                          onStart: function () {
                            O &&
                              e &&
                              dispatch(b.SHOW_FIRE_BALL, { data: d.posId }),
                              d.setSymbolBlurActive(!0);
                          },
                          onComplete: function () {
                            l(t)
                              .to(
                                0.6 * r,
                                { position: new S(h, p, f) },
                                {
                                  easing: "quadOut",
                                  onComplete: function () {
                                    s && s(),
                                      O && e && i.openTimesSymbol(d.posId),
                                      d.setSymbolBlurActive(!1);
                                  },
                                }
                              )
                              .start();
                          },
                        }
                      )
                      .start();
                  }),
                  (s.newFallMoveTo = function (t, o, e) {
                    var n = this.data.getData().symbolPosConfig.get(t),
                      s = n.x,
                      i = n.y,
                      a = n.z,
                      l = this.symbolsMap.get(t);
                    l.node.setPosition(new S(s, i + this.GAME_HEIGHT, a)),
                      (l.node.active = !0),
                      l.symbolID == f.SCATTER && l.playScatterInBtmFast(),
                      this.moveTo(l.node, t, !0, o, e);
                  }),
                  (s.showNewSymbolFall = function (t) {
                    for (
                      var o = this.data.getData().parser.view1D,
                        e = Array.from(this.symbolsMap.keys()),
                        n = Array.from({ length: o.length }, function (t, o) {
                          return o;
                        })
                          .filter(function (t) {
                            return !e.includes(t);
                          })
                          .sort(function (t, o) {
                            return t - o;
                          }),
                        s = 0,
                        i = 0;
                      i < this.SYMBOL_ROW;
                      i++
                    )
                      for (
                        var a = this.TOTAL_SYMBOL - this.SYMBOL_ROW + i;
                        a >= 0;
                        a -= this.SYMBOL_ROW
                      )
                        if (n.includes(a)) {
                          s++;
                          var l = o[a],
                            r = s == n.length ? t : null;
                          this.createSymbol(a, l, !1),
                            this.newFallMoveTo(a, i, r);
                        }
                  }),
                  (s.openTimesSymbol = function (t) {
                    this.symbolsMap.get(t).openTimesSymbol(t);
                  }),
                  (s.hideTimesSymbolLabel = function (t) {
                    this.symbolsMap.get(t).closeTimesLabel();
                  }),
                  (s.playTimesSymbolsFunction = function (t) {
                    this.symbolsMap.get(t).playTimesSymbolsFunction();
                  }),
                  (s.startQuickStop = function (t) {
                    if (
                      (this.unscheduleAllCallbacks(),
                      dispatch(b.SET_EARLY_SPIN_DELAYING_COMPLETED),
                      this.isOutCompleted)
                    )
                      r.stopAllByTag(this.symbolInTag), t();
                    else {
                      r.stopAllByTag(this.symbolOutTag),
                        this.isStartSymbolIn &&
                          (r.stopAllByTag(this.symbolInTag),
                          (this.isStartSymbolIn = !1));
                      var o = this.node.getComponentsInChildren(u);
                      if (o.length > 0)
                        for (var e = 0; e < o.length; e++) o[e].recycleSymbol();
                      for (var n = 0; n < this.TOTAL_SYMBOL; n++) {
                        var s = this.symbolsMap.get(n);
                        s && (s.recycleSymbol(), this.symbolsMap.delete(n)),
                          n == this.TOTAL_SYMBOL - 1 && t();
                      }
                      this.createSymbols(!1),
                        (this.isOutCompleted = !0),
                        (this.needInitHeight = !0);
                    }
                  }),
                  (s.reset = function () {}),
                  (s.init = function () {}),
                  (s.show = function () {
                    this.node.active = !0;
                  }),
                  (s.hide = function () {
                    this.node.active = !1;
                  }),
                  (s.addEvents = function () {
                    var t = this;
                    this.on(O.CLICK_GAME_LOADING_CONFIRM_BTN, function () {
                      t.createSymbols(!0);
                    }),
                      this.on(b.PARSER_REPLAY_COMPLETED, function () {
                        t.createSymbols(!0);
                      }),
                      this.on(b.SHOW_SYMBOLS_OUT_ANIM, function (o) {
                        t.symbolsMap.forEach(function (o, e) {
                          t.oldSymbolsMap.set(e, o);
                        }),
                          t.symbolsMap.clear(),
                          t.showSymbolsOut(o.complete);
                      }),
                      this.on(b.SHOW_SYMBOLS_IN_ANIM, function (o) {
                        0 == t.isOutCompleted
                          ? t.schedule(function () {
                              1 == t.isOutCompleted &&
                                (t.unscheduleAllCallbacks(),
                                (t.isStartSymbolIn = !0),
                                t.createSymbols(!1),
                                t.showSymbolsIn(o.complete));
                            }, 0.001)
                          : ((t.isStartSymbolIn = !0),
                            t.createSymbols(!1),
                            t.showSymbolsIn(o.complete));
                      }),
                      this.on(b.SHOW_SYMBOLS_WIN, function (o) {
                        t.playSymbolsWin(o.complete);
                      }),
                      this.on(b.REMOVE_SYMBOLS, function (o) {
                        t.playOutAnimAndRemoveSymbols(o.complete);
                      }),
                      this.on(b.PLAY_CURRENT_VIEW_FALL_ANIM, function (o) {
                        t.showCurrentViewFall(o.complete);
                      }),
                      this.on(b.SHOW_NEW_SYMBOLS_IN_ANIM, function (o) {
                        t.showNewSymbolFall(o.complete),
                          t.setSymbolsSiblingIndex();
                      }),
                      this.on(b.SHOW_SCATTER_WIN, function (o) {
                        t.playScatterWin(o.complete);
                      }),
                      this.on(b.SHOW_JP_WIN, function (o) {
                        t.playJpWin(o.complete);
                      }),
                      this.on(b.SHOW_TIMES_SYMBOLS_UPGRADE, function () {
                        t.playRareUpgrade();
                      }),
                      this.on(b.HIDE_TIMES_LABEL, function (o) {
                        t.hideTimesSymbolLabel(o.data);
                      }),
                      this.on(b.PLAY_TIMES_SYMBOL_FUNCTION, function (o) {
                        t.playTimesSymbolsFunction(o.data);
                      }),
                      this.on(b.START_QUICK_STOP, function (o) {
                        t.startQuickStop(o.complete);
                      }),
                      this.on(b.SHOW_SYMBOLS_QUICK_IN_ANIM, function (o) {
                        t.showSymbolsQuickIn(o.complete);
                      }),
                      this.on(O.KILL_SYMBOLS, function () {
                        t.killSymbols();
                      });
                  }),
                  e(n, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(p);
                      },
                    },
                    {
                      key: "configModel",
                      get: function () {
                        return y.getData();
                      },
                    },
                  ]),
                  n
                );
              })(m))
            ) || M
          );
        n._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/TransitionView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./Decorators.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./GameConfigModel.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var n, i, e, o, a, s, r, c, u, p, l, h, d, f, S;
    return {
      setters: [
        function (t) {
          (n = t.applyDecoratedDescriptor),
            (i = t.inheritsLoose),
            (e = t.initializerDefineProperty),
            (o = t.assertThisInitialized),
            (a = t.createClass);
        },
        function (t) {
          (s = t.cclegacy), (r = t._decorator), (c = t.sp), (u = t.v3);
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          l = t.inject;
        },
        function (t) {
          h = t.default;
        },
        function (t) {
          d = t.GameEvent;
        },
        function (t) {
          f = t.EBTM;
        },
        function (t) {
          S = t.default;
        },
      ],
      execute: function () {
        var T, v, g, y, m;
        s._RF.push({}, "345805QIlxLM5OFBN8QZW5r", "TransitionView", void 0);
        var w = r.ccclass;
        r.property,
          t(
            "TransitionView",
            ((T = w("TransitionView")),
            (v = l("transitionSpine", c.Skeleton)),
            T(
              ((m = n(
                (y = (function (t) {
                  function n() {
                    for (
                      var n, i = arguments.length, a = new Array(i), s = 0;
                      s < i;
                      s++
                    )
                      a[s] = arguments[s];
                    return (
                      (n = t.call.apply(t, [this].concat(a)) || this),
                      e(n, "transitionSpine", m, o(n)),
                      n
                    );
                  }
                  i(n, t);
                  var s = n.prototype;
                  return (
                    (s.onLoad = function () {
                      t.prototype.onLoad.call(this);
                    }),
                    (s.start = function () {
                      this.init();
                    }),
                    (s.onDestroy = function () {
                      t.prototype.onDestroy.call(this);
                    }),
                    (s.init = function () {}),
                    (s.showTransitionIn = function (t) {
                      var n = this;
                      (this.transitionSpine.node.active = !0),
                        "portrait" == S.getViewModeParam() &&
                          ((this.transitionSpine.node.scale = u(
                            1.2,
                            -1.2,
                            1.2
                          )),
                          (this.transitionSpine.node.angle = 90)),
                        (this.transitionSpine.skeletonData =
                          this.data.getTransitionSpine("transition_in")),
                        this.transitionSpine.setAnimation(0, "in", !1),
                        this.transitionSpine.setCompleteListener(function () {
                          n.transitionSpine.node.active = !1;
                        }),
                        dispatch(d.PLAY_BTM, { data: { url: f.TRANSITION } }),
                        this.scheduleOnce(t, 1);
                    }),
                    (s.showTransitionOut = function (t) {
                      var n = this;
                      (this.transitionSpine.node.active = !0),
                        "portrait" == S.getViewModeParam() &&
                          ((this.transitionSpine.node.scale = u(
                            1.2,
                            -1.2,
                            1.2
                          )),
                          (this.transitionSpine.node.angle = 90)),
                        (this.transitionSpine.skeletonData =
                          this.data.getTransitionSpine("transition_out")),
                        this.transitionSpine.setAnimation(0, "out", !1),
                        this.transitionSpine.setCompleteListener(function () {
                          n.transitionSpine.node.active = !1;
                        }),
                        dispatch(d.PLAY_BTM, { data: { url: f.TRANSITION } }),
                        this.scheduleOnce(t, 1);
                    }),
                    (s.reset = function () {}),
                    (s.setData = function (t) {}),
                    (s.show = function () {
                      this.node.active = !0;
                    }),
                    (s.hide = function () {
                      (this.node.active = !1),
                        (this.transitionSpine.node.scale = u(1, 1, 1)),
                        (this.transitionSpine.node.angle = 0);
                    }),
                    (s.addEvents = function () {
                      var t = this;
                      this.on(d.SHOW_TRANSITION_IN, function (n) {
                        t.showTransitionIn(n.data);
                      }),
                        this.on(d.SHOW_TRANSITION_OUT, function (n) {
                          t.showTransitionOut(n.data);
                        });
                    }),
                    a(n, [
                      {
                        key: "data",
                        get: function () {
                          return App.dataCenter.get(h);
                        },
                      },
                    ]),
                    n
                  );
                })(p)).prototype,
                "transitionSpine",
                [v],
                {
                  configurable: !0,
                  enumerable: !0,
                  writable: !0,
                  initializer: function () {
                    return null;
                  },
                }
              )),
              (g = y))
            ) || g)
          );
        s._RF.pop();
      },
    };
  }
);

System.register(
  "chunks:///_virtual/TreasuresView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./UIView.ts",
    "./GameEvent.ts",
    "./GameConfigModel.ts",
    "./CmmSlotUtils.ts",
    "./Decorators.ts",
    "./GameData.ts",
    "./SlotFrameworkEvent.ts",
    "./MathUtil.ts",
    "./UrlUtils.ts",
  ],
  function (t) {
    "use strict";
    var e,
      i,
      n,
      a,
      o,
      s,
      l,
      c,
      r,
      u,
      h,
      d,
      p,
      f,
      _,
      T,
      S,
      m,
      w,
      B,
      N,
      O,
      g,
      y,
      W;
    return {
      setters: [
        function (t) {
          (e = t.applyDecoratedDescriptor),
            (i = t.inheritsLoose),
            (n = t.initializerDefineProperty),
            (a = t.assertThisInitialized),
            (o = t.createClass);
        },
        function (t) {
          (s = t.cclegacy),
            (l = t._decorator),
            (c = t.Node),
            (r = t.sp),
            (u = t.Tween),
            (h = t.tween),
            (d = t.NodeEventType),
            (p = t.Vec3),
            (f = t.KeyCode),
            (_ = t.Label);
        },
        function (t) {
          T = t.default;
        },
        function (t) {
          S = t.GameEvent;
        },
        function (t) {
          (m = t.EBTM), (w = t.default);
        },
        function (t) {
          B = t.CmmSlotUtils;
        },
        function (t) {
          N = t.inject;
        },
        function (t) {
          O = t.default;
        },
        function (t) {
          g = t.SlotFrameworkEvent;
        },
        function (t) {
          y = t.default;
        },
        function (t) {
          W = t.default;
        },
      ],
      execute: function () {
        var A, P, C, b, I, E, M, U, v, L, D, R, G, k, V;
        s._RF.push({}, "8aa14oMcU9NkqZLu7MuIsrF", "TreasuresView", void 0);
        var H,
          z = l.ccclass,
          F = l.property;
        !(function (t) {
          (t[(t.NONE = 0)] = "NONE"),
            (t[(t.SHOW_BIGWIN = 1)] = "SHOW_BIGWIN"),
            (t[(t.SHOW_BUGWIN_NUMBER = 2)] = "SHOW_BUGWIN_NUMBER"),
            (t[(t.SHOW_BUGWIN_NUMBER_END = 3)] = "SHOW_BUGWIN_NUMBER_END"),
            (t[(t.BIGWIN_COMPLETED = 4)] = "BIGWIN_COMPLETED");
        })(H || (H = {}));
        t(
          "TreasuresView",
          ((A = z("TreasuresView")),
          (P = N("alert", c)),
          (C = F(c)),
          (b = N("alert/effectBg", r.Skeleton)),
          (I = N("alert/totalWin", _)),
          (E = N("alert/fireworks", r.Skeleton)),
          (M = N("alert/coinSprays", c)),
          A(
            ((L = e(
              (v = (function (t) {
                function e() {
                  for (
                    var e, i = arguments.length, o = new Array(i), s = 0;
                    s < i;
                    s++
                  )
                    o[s] = arguments[s];
                  return (
                    (e = t.call.apply(t, [this].concat(o)) || this),
                    n(e, "alert", L, a(e)),
                    n(e, "bbr", D, a(e)),
                    n(e, "effectBg", R, a(e)),
                    n(e, "totalWin", G, a(e)),
                    n(e, "fireworks", k, a(e)),
                    n(e, "coinSprays", V, a(e)),
                    (e.bigwinFontFileNames = [
                      "w_big",
                      "w_super",
                      "w_mega",
                      "w_ultra",
                      "w_legend",
                    ]),
                    (e.complete = null),
                    (e.completedCB = null),
                    (e.tweenNumTween = null),
                    (e.bigwinVO = null),
                    (e.playBigFontLoop = null),
                    (e.showWinStatus = H.NONE),
                    (e.playPrizeLoopBtmSchedule = null),
                    (e.playPrizeVoiceBtmSchedule = null),
                    e
                  );
                }
                i(e, t),
                  (e.getPrefabUrl = function () {
                    return "prefabs/" + W.getViewModeParam() + "/TreasuresView";
                  });
                var s = e.prototype;
                return (
                  (s.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (s.start = function () {
                    this.init();
                  }),
                  (s.onDestroy = function () {
                    this.stopAllMusicAndSchedule(),
                      t.prototype.onDestroy.call(this);
                  }),
                  (s.init = function () {
                    this.enabledKeyDown = !0;
                  }),
                  (s.show = function (e) {
                    t.prototype.show.call(this);
                  }),
                  (s.onClose = function () {
                    this.unscheduleAllCallbacks(),
                      u.stopAllByTarget(this),
                      this.closeNodes(),
                      this.stopAllMusicAndSchedule(),
                      (App.globalAudio.isMusicOn = !0),
                      App.globalAudio.resumeMusic();
                    var t = this.data.getData().gameState.noWinReward;
                    dispatch(S.QUICK_STOP_TOTAL_WINNINGS, { data: t }),
                      dispatch(S.QUICK_STOP_WIN_AMOUNT, { data: t }),
                      this.close();
                  }),
                  (s.stopAllMusicAndSchedule = function () {
                    dispatch(S.STOP_BTM, { data: m.JP_POPUP_IN_2 }),
                      dispatch(S.STOP_BTM, { data: m.JP_POPUP_LOOP_2 }),
                      dispatch(S.STOP_BTM, { data: m.ULTRA_IN }),
                      dispatch(S.STOP_BTM, { data: m.LEGEND_IN }),
                      dispatch(S.STOP_BTM, { data: m.S_PRIZE_LOOP }),
                      dispatch(S.STOP_BTM, { data: m.L_PRIZE_LOOP }),
                      dispatch(S.STOP_BTM, { data: m.FIREWORKS }),
                      dispatch(S.STOP_BTM, { data: m.BIG_VOCAL }),
                      dispatch(S.STOP_BTM, { data: m.SUPER_VOCAL }),
                      dispatch(S.STOP_BTM, { data: m.MEGA_VOCAL }),
                      dispatch(S.STOP_BTM, { data: m.ULTRA_VOCAL }),
                      dispatch(S.STOP_BTM, { data: m.LEGENDARY_VOCAL }),
                      this.unschedule(this.playPrizeLoopBtmSchedule),
                      this.unschedule(this.playPrizeVoiceBtmSchedule);
                  }),
                  (s.closeNodes = function () {
                    this.bbr && (this.bbr.active = !1),
                      (this.effectBg.node.active = !1),
                      (this.totalWin.node.active = !1),
                      (this.fireworks.node.active = !1),
                      (this.coinSprays.active = !1),
                      this.coinSprays.children.forEach(function (t) {
                        t.active = !1;
                      }),
                      this.alert.targetOff(this);
                  }),
                  (s.playAnimation = function (t) {
                    App.globalAudio.pauseMusic(), this.playWin(t);
                  }),
                  (s.playWin = function (t) {
                    var e = this,
                      i = w.getData().bigwinAutoCloseTime;
                    (this.effectBg.node.active = !0),
                      this.effectBg.clearTracks(),
                      this.effectBg.setToSetupPose(),
                      dispatch(S.PLAY_BTM, {
                        data: { url: m.JP_POPUP_IN_2, loop: !1 },
                      }),
                      this.effectBg.setAnimation(0, "in", !1),
                      this.effectBg.setCompleteListener(function () {
                        e.effectBg.setCompleteListener(null),
                          e.effectBg.setAnimation(0, "open", !1),
                          h(e)
                            .delay(0.5)
                            .call(function () {
                              dispatch(S.PLAY_BTM, {
                                data: { url: m.JP_POPUP_LOOP_2, loop: !0 },
                              }),
                                e.playCoinSprayAndRunScore();
                            })
                            .start(),
                          e.effectBg.setCompleteListener(function () {
                            e.effectBg.setCompleteListener(null),
                              e.effectBg.setAnimation(0, "loop", !0);
                          });
                      }),
                      this.scheduleOnce(this.showWinResult, i + t);
                  }),
                  (s.playCoinSprayAndRunScore = function () {
                    var t = this,
                      e = this.data.getData().gameState.noWinReward,
                      i = this.data.getData().definition.digital;
                    dispatch(g.UPDATE_TOTAL_WINNINGS, {
                      data: { value: e, tweenTime: 8 },
                    }),
                      dispatch(S.UPDATE_WIN_AMOUNT, {
                        data: { value: e, tweenTime: 8 },
                      }),
                      this.showCoinSpray();
                    var n = {
                      label: this.totalWin,
                      start: 0,
                      end: e,
                      tweenTime: 8,
                      digital: i,
                      useThousandsSeparator: !0,
                    };
                    (this.showWinStatus = H.SHOW_BUGWIN_NUMBER),
                      (this.totalWin.node.active = !0),
                      (this.tweenNumTween = B.tweenNum(n)),
                      this.alert.once(
                        d.TOUCH_END,
                        function () {
                          t.showWinResult();
                        },
                        this
                      );
                  }),
                  (s.addClickAlertCompleteCb = function () {
                    this.unschedule(this.addClickAlertCompleteCb),
                      this.alert.once(d.TOUCH_END, this.completedCB);
                    var t = w.getData().bigwinAutoCloseTime;
                    this.scheduleOnce(this.completedCB, t);
                  }),
                  (s.playBounceTween = function (t, e) {
                    h(t)
                      .to(0.1, { scale: new p(1.8, 1.8, 1.8) })
                      .delay(0.01)
                      .to(
                        0.1,
                        { scale: new p(1, 1, 1) },
                        {
                          onComplete: function () {
                            e && e();
                          },
                        }
                      )
                      .start();
                  }),
                  (s.showCoinSpray = function () {
                    var t = this,
                      e = this.coinSprays.getComponentsInChildren(r.Skeleton);
                    this.coinSprays.active = !0;
                    for (
                      var i = function () {
                          var i = e[n];
                          0 == n
                            ? ((i.node.active = !0),
                              i.setAnimation(0, "coin_01", !1))
                            : 1 == n
                            ? t.scheduleOnce(function () {
                                (i.node.active = !0),
                                  i.setAnimation(0, "coin_02", !1);
                              }, 1.3)
                            : t.scheduleOnce(function () {
                                var t = y.getRandomNumber(3, 6);
                                (i.node.active = !0),
                                  i.setAnimation(0, "radom_0" + t, !1),
                                  i.setCompleteListener(function () {
                                    var t = y.getRandomNumber(3, 6);
                                    i.setAnimation(0, "radom_0" + t, !1);
                                  });
                              }, 2.8 + 0.5 * (n - 2));
                        },
                        n = 0;
                      n < e.length;
                      n++
                    )
                      i();
                  }),
                  (s.showWinResult = function () {
                    var t = this.data.getData().gameState.noWinReward;
                    u.stopAllByTarget(this),
                      this.tweenNumTween && this.tweenNumTween.stop(),
                      (this.totalWin.string = B.formatNumber(t)),
                      this.playBounceTween(this.totalWin.node),
                      this.unschedule(this.playBigFontLoop),
                      dispatch(S.QUICK_STOP_TOTAL_WINNINGS, { data: t }),
                      dispatch(S.QUICK_STOP_WIN_AMOUNT, { data: t }),
                      this.unschedule(this.showWinResult),
                      this.addClickAlertCompleteCb();
                  }),
                  (s.showTreasureWin = function (t) {
                    var e = this;
                    (this.totalWin.string = "0.00"),
                      (this.showWinStatus = H.SHOW_BIGWIN),
                      (this.completedCB = function () {
                        (e.showWinStatus = H.BIGWIN_COMPLETED),
                          t(),
                          e.onClose(),
                          e.unschedule(e.playBigFontLoop);
                      }),
                      App.globalAudio.pauseMusic(),
                      (App.globalAudio.isMusicOn = !1),
                      h(this)
                        .delay(1)
                        .call(function () {
                          (e.bbr.active = !0),
                            h(e)
                              .delay(1)
                              .call(function () {
                                e.playAnimation(8);
                              })
                              .start();
                        })
                        .start();
                  }),
                  (s.onKeyDown = function (e) {
                    if (
                      (t.prototype.onKeyDown.call(this, e),
                      e.keyCode === f.SPACE)
                    )
                      switch (this.showWinStatus) {
                        case H.SHOW_BUGWIN_NUMBER:
                          this.showWinStatus = H.SHOW_BUGWIN_NUMBER_END;
                          break;
                        case H.SHOW_BUGWIN_NUMBER_END:
                          (this.showWinStatus = H.BIGWIN_COMPLETED),
                            this.scheduleOnce(this.completedCB, 0.5);
                      }
                  }),
                  (s.addEvents = function () {}),
                  o(e, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(O);
                      },
                    },
                  ]),
                  e
                );
              })(T)).prototype,
              "alert",
              [P],
              {
                configurable: !0,
                enumerable: !0,
                writable: !0,
                initializer: function () {
                  return null;
                },
              }
            )),
            (D = e(v.prototype, "bbr", [C], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (R = e(v.prototype, "effectBg", [b], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (G = e(v.prototype, "totalWin", [I], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (k = e(v.prototype, "fireworks", [E], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (V = e(v.prototype, "coinSprays", [M], {
              configurable: !0,
              enumerable: !0,
              writable: !0,
              initializer: function () {
                return null;
              },
            })),
            (U = v))
          ) || U)
        );
        s._RF.pop();
      },
    };
  }
);

System.register("chunks:///_virtual/types.ts", ["cc"], function (o) {
  "use strict";
  var e;
  return {
    setters: [
      function (o) {
        e = o.cclegacy;
      },
    ],
    execute: function () {
      var i, t;
      o({ EGameType: void 0, EPool: void 0 }),
        e._RF.push({}, "66f05P3M5tEY7khCobGW8zV", "types", void 0),
        (function (o) {
          (o.SYMBOL_POOL = "symbolPool"),
            (o.FIREBALL_POOL = "fireballPool"),
            (o.TIMES_MOVING_POOL = "timesMovingPool"),
            (o.PURPLE_TIMES_MOVING_POOL = "purpleTimesMovingPool"),
            (o.BLUE_TIMES_MOVING_POOL = "blueTimesMovingPool"),
            (o.WIN_CASH_POOL = "winCashPool");
        })(i || (i = o("EPool", {}))),
        (function (o) {
          (o.MAIN_GAME = "mainGame"), (o.FREE_GAME = "freeGame");
        })(t || (t = o("EGameType", {}))),
        e._RF.pop();
    },
  };
});

System.register(
  "chunks:///_virtual/WinView.ts",
  [
    "./rollupPluginModLoBabelHelpers.js",
    "cc",
    "./EventComponent.ts",
    "./CmmSlotUtils.ts",
    "./GameConfigModel.ts",
    "./GameData.ts",
    "./GameEvent.ts",
    "./types.ts",
  ],
  function (t) {
    "use strict";
    var n, o, e, i, a, s, c, r, f, u, l, p, h, d;
    return {
      setters: [
        function (t) {
          (n = t.inheritsLoose), (o = t.createClass);
        },
        function (t) {
          (e = t.cclegacy),
            (i = t._decorator),
            (a = t.instantiate),
            (s = t.Label),
            (c = t.tween),
            (r = t.Vec3);
        },
        function (t) {
          f = t.default;
        },
        function (t) {
          u = t.CmmSlotUtils;
        },
        function (t) {
          l = t.default;
        },
        function (t) {
          p = t.default;
        },
        function (t) {
          h = t.GameEvent;
        },
        function (t) {
          d = t.EPool;
        },
      ],
      execute: function () {
        var g;
        e._RF.push({}, "d31c4gFP99Ha6Osz8u0Vd70", "WinView", void 0);
        var C = i.ccclass;
        i.property,
          t(
            "WinView",
            C("WinView")(
              (g = (function (t) {
                function e() {
                  return t.apply(this, arguments) || this;
                }
                n(e, t);
                var i = e.prototype;
                return (
                  (i.onLoad = function () {
                    t.prototype.onLoad.call(this);
                  }),
                  (i.start = function () {
                    this.init();
                  }),
                  (i.onDestroy = function () {
                    t.prototype.onDestroy.call(this);
                  }),
                  (i.init = function () {
                    this.createWinCashPool();
                  }),
                  (i.createWinCashPool = function () {
                    for (
                      var t = l.getData().filePaths.winCashPrefab,
                        n = App.cache.get(this.data.module, t).data,
                        o = 0;
                      o < 2;
                      o++
                    ) {
                      var e = a(n);
                      (App.pool.createPool(d.WIN_CASH_POOL).cloneNode = e),
                        App.pool.createPool(d.WIN_CASH_POOL).put(e);
                    }
                  }),
                  (i.showWinCash = function () {
                    var t = this,
                      n = this.data.getData().gameState.winSymbols,
                      o = [
                        14, 15, 8, 9, 20, 21, 2, 3, 26, 27, 13, 16, 7, 10, 19,
                        22, 1, 4, 25, 28, 12, 17, 6, 11, 18, 23, 0, 5, 24, 29,
                      ];
                    n.forEach(function (n) {
                      var e = [];
                      n.symbolPos.forEach(function (t) {
                        e.push(o.indexOf(t));
                      }),
                        e.sort(function (t, n) {
                          return t - n;
                        });
                      var i = App.pool.getPool(d.WIN_CASH_POOL).get(),
                        a = o[e[0]],
                        c = i.getComponent(s);
                      (i.active = !1),
                        t.node.addChild(i),
                        (c.string = u.formatNumber(n.winnings)),
                        t.playWinCashTween(i, a);
                    });
                  }),
                  (i.playWinCashTween = function (t, n) {
                    var o = this.data.getData().symbolPosConfig.get(n),
                      e = t.getComponent(s).color;
                    e.fromHEX("#ffffff"),
                      c(t)
                        .set({ position: o, active: !0 })
                        .by(
                          1.5,
                          { position: new r(0, 50, 0) },
                          {
                            easing: "fade",
                            onComplete: function () {
                              App.pool.getPool(d.WIN_CASH_POOL).put(t);
                            },
                          }
                        )
                        .start(),
                      c(e)
                        .delay(1)
                        .to(0.5, { a: 0 }, { easing: "fade" })
                        .start();
                  }),
                  (i.reset = function () {}),
                  (i.setData = function (t) {}),
                  (i.show = function () {
                    this.node.active = !0;
                  }),
                  (i.hide = function () {
                    this.node.active = !1;
                  }),
                  (i.addEvents = function () {
                    var t = this;
                    this.on(h.SHOW_WIN_CASH, function () {
                      t.showWinCash();
                    });
                  }),
                  o(e, [
                    {
                      key: "data",
                      get: function () {
                        return App.dataCenter.get(p);
                      },
                    },
                  ]),
                  e
                );
              })(f))
            ) || g
          );
        e._RF.pop();
      },
    };
  }
);

(function (r) {
  r("virtual:///prerequisite-imports/g1001", "chunks:///_virtual/g1001");
})(function (mid, cid) {
  System.register(mid, [cid], function (_export, _context) {
    return {
      setters: [
        function (_m) {
          var _exportObj = {};

          for (var _key in _m) {
            if (_key !== "default" && _key !== "__esModule")
              _exportObj[_key] = _m[_key];
          }

          _export(_exportObj);
        },
      ],
      execute: function () {},
    };
  });
});
