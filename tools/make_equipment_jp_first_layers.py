from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BOSS_NAMES = {
    "マルス": "玛尔斯",
    "リカオン": "吕卡翁",
    "ミノス": "米诺斯",
    "ブリアレオス": "布里阿瑞俄斯",
    "スピンクス": "斯芬克斯",
    "アルクマイオン": "阿尔克迈翁",
    "グリュプス": "格律普斯",
    "スタティウス": "斯塔提乌斯",
    "黄金GRAM": "黄金GRAM",
}

PART_NAMES = {
    "頭": "头部",
    "右腕": "右臂",
    "左腕": "左臂",
    "右手": "右手",
    "胸": "胸部",
    "脚": "腿部",
}

CLAUSE_TRANSLATIONS = {
    "上段叩き付け。": "上段叩击。",
    "相手を叩きつける事がある。": "有时可将敌人砸倒。",
    "ブルース・リー裏拳攻撃。物理スタン。": "李小龙式背拳攻击。造成物理眩晕。",
    "ボディアッパー。浮かし攻撃": "身体上勾拳。挑空攻击。",
    "鉄山靠。": "铁山靠。",
    "相手をノックバック＆吹き飛ばす。": "可击退并吹飞敌人。",
    "近接攻撃用のクロー。2枚の超振動ブレードを備える。": "近战用爪，配备两片超振动刀刃。",
    "コンボ攻撃を行うことでより大きなダメージを与えることができる。": "通过连击可造成更大伤害。",
    "大きな角状の打突武装。": "大型角状突击武装。",
    "接触時に高速に振動することでダメージを増加させる。": "接触瞬间高速振动以提高伤害。",
    "拳に電磁場を発生させ、パンチと共に射出する。": "在拳部生成电磁场，并随拳击一同射出。",
    "リーチ範围外の敵の動きを止め、ダメージを与えることが可能。": "可停止攻击距离外敌人的行动并造成伤害。",
    "電磁シールドを応用し、地表に強力な電磁場を展関する": "应用电磁盾技术，在地表展开强力电磁场。",
    "電子スタン兵器。": "电子眩晕兵器。",
    "電磁場に触れた敵は一定時間行動不能となる。": "触碰电磁场的敌人会在一定时间内无法行动。",
    "巨大なドリルを高速回転させながら敵へ打ち入み、": "让巨大钻头高速旋转并贯入敌人，",
    "強い衝撃とダメージを与える近接武装。": "造成强冲击与伤害的近战武装。",
    "強烈な突進能力と物理スタン効果を有し、": "具备强烈突进能力和物理眩晕效果，",
    "中距離から一気に接近して敵の動きを止める。": "可从中距离一口气接近并停止敌人行动。",
    "頭部に装備するとより効果的に機能する。": "装备在头部时效果更好。",
    "チャージする事でヒット回数が増加する。": "蓄力可增加命中次数。",
    "腕部に装備するとより効果的に機能する。": "装备在臂部时效果更好。",
    "触れた敵に電気ショックを連続して与え、": "对接触的敌人连续施加电击，",
    "一時的に動きを停止させる近接武装。": "使其暂时停止行动的近战武装。",
    "盾やアーマーではガードできない。": "盾牌和装甲无法防御。",
    "触れた敵に大きな電気ショックを与え、": "对接触的敌人施加强力电击，",
    "炸薬で拳から杭を打ち入む近接武装。": "以炸药从拳部打入桩钉的近战武装。",
    "熱上昇が激しく隙も大きいが、非常に強力なノックバック、": "发热剧烈且破绽很大，但拥有极强击退，",
    "吹き飛ばし効果を有する。": "并具备吹飞效果。",
    "コンボ攻撃を行うことで绝大なダメージを与えることが可能。": "通过连击可造成极大伤害。",
    "一撃目で敵の動きを止め、二撃目で敵の装備を": "第一击停止敌人行动，第二击使敌方装备",
    "エネルギー切れにする。": "陷入能量耗尽。",
    "赤熱化した裏拳で敵を叩きつけ、熱量値を上昇させる近接武装。": "以赤热背拳砸击敌人并提高热量值的近战武装。",
    "コンボ攻撃に組み入みやすい。": "容易编入连击。",
    "赤熱化した拳で敵を打ち上げ、熱量値を上昇させる近接武装。": "以赤热拳头击飞敌人并提高热量值的近战武装。",
    "指輪の形をした特殊な武装カプセル": "戒指形特殊武装胶囊。",
    "2006.1.6 to Beatie": "2006.1.6 to Beatie",
    "近接攻撃用の刀剣。": "近战用刀剑。",
    "外見は原始的だが、超振動ブレードの採用により、": "外观原始，但采用超振动刀刃后，",
    "強化樹脂をも切り裂く。": "甚至可切裂强化树脂。",
    "攻撃範围が応く、攻撃時にガード効果を持つ安定した武装。": "攻击范围广，攻击时带防御效果，是稳定武装。",
    "三連続攻撃で高い攻撃力を発揮する。": "三连击可发挥高攻击力。",
    "七連続攻撃で高い攻撃力を発揮する。": "七连击可发挥高攻击力。",
    "敵と離れていても一気に間合いを詰めることができる。": "即使与敌人相隔较远，也可一口气拉近距离。",
    "クリティカルにより敵の耐久力を半分にすることがある。": "暴击时有时可将敌人耐久减半。",
    "クリティカルにより敵の耐久力を半分にする。": "暴击会将敌人耐久减半。",
    "肉厚の刀身を持つ、観客に向けたショー的要素の強い巨大剣。": "厚重刀身的巨剑，带有强烈面向观众的表演性。",
    "攻撃速度は遅いが、応い攻撃範围と高い浮かし能力を持つ。": "攻击速度慢，但攻击范围广，挑空能力高。",
    "大きく振り回して敵をなぎ倒す近接武装。": "大幅挥舞并扫倒敌人的近战武装。",
    "攻撃速度は遅いが、応い攻撃範围と高い叩き付け能力を持つ。": "攻击速度慢，但攻击范围广，砸倒能力高。",
    "大きく振り回して敵を背後へ吹き飛ばす近接武装。": "大幅挥舞并将敌人吹飞到背后的近战武装。",
    "大きく振り回して打突による衝撃でダメージを与える近接武装。": "大幅挥舞，以打突冲击造成伤害的近战武装。",
    "敵の装備をエネルギー切れにすることがある。": "有时可使敌方装备能量耗尽。",
    "近接攻撃用の剣。": "近战用剑。",
    "ダメージに加え、攻撃した相手の熱量値を上昇させる。": "除造成伤害外，还会提高被攻击目标的热量值。",
    "攻撃の際に敵に向かってジャンプして接近する。": "攻击时会跳向敌人并接近。",
    "近接攻撃用の斧。攻撃速度は遅いがダメージは大きい。": "近战用斧。攻击速度慢，但伤害很高。",
    "攻撃した相手の熱量値を上昇させる。": "会提高被攻击目标的热量值。",
    "回転攻撃で周围の敵を薙ぎ払い、吹き飛ばす二段攻撃。": "以旋转攻击横扫周围敌人并吹飞的二段攻击。",
    "回転攻撃で周围の敵を薙ぎ払い、吹き飛ばす三段攻撃。": "以旋转攻击横扫周围敌人并吹飞的三段攻击。",
    "超高速回転攻撃で周围の敵を薙ぎ払い、吹き飛ばす": "以超高速旋转攻击横扫并吹飞周围敌人，",
    "覧異の八段攻撃。": "是惊异的八段攻击。",
    "エネルギー消費は激しいが、攻撃力の高い近接用の武装。": "能量消耗剧烈，但攻击力很高的近战武装。",
    "プラズマが超高温の刃と化し、対象を瞬時に焼き切る。": "等离子化为超高温刀刃，瞬间烧断目标。",
    "無数の細かい刃が超振動しながら回転し、": "无数细小刀刃一边超振动一边旋转，",
    "ダメージを与える近接武装。": "造成伤害的近战武装。",
    "攻撃中でも移動可能で、さらに攻撃している敵を引き付ける。": "攻击中也可移动，并会牵引正在攻击的敌人。",
    "旧世紀のハンドガンをモチーフに、ADAM用に大口径化された": "以旧世纪手枪为原型，为ADAM放大口径的",
    "モンスターガン。": "怪物手枪。",
    "ADAMの武装としては最小火力の部類に属する。": "在ADAM武装中属于最低火力级别。",
    "攻撃ボタンを押しつづけることで連射可能。": "按住攻击键可连续射击。",
    "旧世紀のハンドガンをモチーフに、防御不能の化学反応弾を": "以旧世纪手枪为原型，发射无法防御的化学反应弹的",
    "発射する禁断のカスタムガン。": "禁断改造枪。",
    "敵の装備をエネルギー切れにする。": "使敌方装备能量耗尽。",
    "弾数は少ない。": "弹数较少。",
    "超硬度、高密度の矢を連続して射出する強力なボウガン。": "连续射出超硬度、高密度箭矢的强力弩。",
    "時代遅れではあるが、火力、弾数、発熱量のバランスが良く": "虽已过时，但火力、弹数与发热量平衡良好，",
    "兵器としての有用性は色あせていない。": "作为兵器的实用性仍未褪色。",
    "ユニットを大型化することで火力と弾数が増加している。": "通过大型化单元提高了火力与弹数。",
    "弾速が速く攻撃力も高いが、隙が大きいライフル。": "弹速快、攻击力高，但破绽很大的步枪。",
    "小さいながらも超高密度の弾丸を多数射出する散弾銃。": "体积虽小，却可射出大量超高密度弹丸的霰弹枪。",
    "近距離ほど大きなダメージを与えることができる。": "距离越近，造成的伤害越大。",
    "スタン効果の高い電磁針を連続して射出する。": "连续射出眩晕效果高的电磁针。",
    "この電磁針は敵を貫通する。": "这种电磁针会贯穿敌人。",
    "攻撃力はそこそこだが、連射性能が高く扱いやすいマシンガン。": "攻击力尚可，但连射性能高、易于使用的机枪。",
    "連続使用してもオーバーヒートしにくい。": "连续使用也不易过热。",
    "超硬度の高速弾を使用するマシンガン。": "使用超硬度高速弹的机枪。",
    "弾は敵を貫通する。": "子弹会贯穿敌人。",
    "短いレーザーを連続して発射する電子機閲銃。": "连续发射短激光的电子机枪。",
    "レーザーは敵を貫通し、壁にあたると反射する。": "激光会贯穿敌人，击中墙壁后反射。",
    "強力な弾丸を高速にばらまく重機閲銃。": "高速倾泻强力弹丸的重机枪。",
    "射撃中は移動速度が半滅する。": "射击中移动速度减半。",
    "着弾すると多数の小型爆弾が拡散そして爆発し、": "着弹后大量小型炸弹扩散并爆炸，",
    "周围の敵に大きなダメージを与える。": "对周围敌人造成巨大伤害。",
    "強力だが反動が大きく、オーバーヒートしやすい。": "威力强大，但后坐力大且容易过热。",
    "反動を押さえて扱いやすくしたロケットランチャー。": "抑制后坐力、便于使用的火箭发射器。",
    "装弾数はさほど多くないが、弾速、破壊力共に優秀。": "装弹数不多，但弹速和破坏力都很优秀。",
    "ドラム式マガジンを備えたグレネードランチャー。": "配备鼓式弹匣的榴弹发射器。",
    "高熱の爆炎により、ダメージに加えて温度も上昇させる。": "以高热爆炎在伤害之外提高温度。",
    "ナパーム弾を射出するグレネードランチャー。": "射出凝固汽油弹的榴弹发射器。",
    "着弾点に炎の海を作り出す。": "在着弹点制造火海。",
    "この炎に包まれるとオーバーヒートは免れない。": "被这种火焰包围便无法避免过热。",
    "炎の海は一定時間経つと消滅する。": "火海会在一定时间后消失。",
    "強力かつ高速なミサイルを射出する。": "射出强力且高速的导弹。",
    "命中時のダメージは绝大。": "命中时伤害极大。",
    "強力かつ高速なミサイルを発射する。命中時のダメージは绝大。": "发射强力且高速的导弹。命中时伤害极大。",
    "ロックオンした敵を自動追尾する小型ミサイルを発射する。": "发射会自动追踪锁定敌人的小型导弹。",
    "ロックオンした敵を自動追尾する小型ミサイルを大量に発射する。": "大量发射会自动追踪锁定敌人的小型导弹。",
    "複数の銃身を回転させながら発砲する、究極の連射武装。": "旋转多根枪管开火的究极连射武装。",
    "オーバーヒートしにくく連続使用も可能だが、射撃時は移動できない。": "不易过热且可连续使用，但射击时无法移动。",
    "超重量の弾丸を磁極の反発を利用して射出するロングライフル。": "利用磁极斥力射出超重量弹丸的长步枪。",
    "威力は绝大だが、連射性能が低い。": "威力极大，但连射性能低。",
    "強力なプラズマ弾を電磁誘導により射出するロングライフル。": "通过电磁诱导射出强力等离子弹的长步枪。",
    "膨大なエネルギーを充填する必要があるため、連射性能が低い。": "由于需要充填庞大能量，连射性能较低。",
    "大型のプラズマ弾を電磁誘導により射出する超大型ライフル。": "通过电磁诱导射出大型等离子弹的超大型步枪。",
    "その破壊力や射出エネルギーはライフルというより大砲に近い。": "其破坏力与射出能量与其说是步枪，更接近大炮。",
    "充填時間によって射出弾数が異なる。": "射出弹数会随充填时间变化。",
    "強烈な電磁波を放出し、周围の電子機器の機能を": "释放强烈电磁波，使周围电子设备的功能",
    "一時的にストップさせる。": "暂时停止。",
    "莫大なエネルギーを一瞬で関放するため、作動時は": "因会瞬间释放庞大能量，发动时",
    "動くことができない。": "无法移动。",
    "マガジン内で振動、増幅された素粒子を連続して射出する。": "连续射出在弹匣内振动并增幅的基本粒子。",
    "威力の高い武器だがオーバーヒートしやすい。": "是威力很高但容易过热的武器。",
    "反物質弾を発射するダブルデリンジャー。": "发射反物质弹的双管德林杰。",
    "あまりに破壊力が大きいため、塔内でも武装供給は停止されている。": "因破坏力过大，即使在塔内也停止供给。",
    "周围の空間から量子を吸収して集め、蓄積されたエネルギーを": "从周围空间吸收并聚集量子，将蓄积的能量",
    "一気に放出する。": "一口气释放。",
    "連射は出来ないが威力は绝大。": "无法连射，但威力极大。",
    "AIセルの重力感知機構を誤動作させる電磁爆弾を射出する。": "射出使AI细胞重力感知机构误动作的电磁炸弹。",
    "浮遊する機雷を前方に射出する。相手が機雷に触れるか、": "向前射出浮游机雷。敌人触碰机雷，或",
    "または一定時間が経過すると爆発する。": "经过一定时间后便会爆炸。",
    "土星型のプラズマボールを射出する。": "射出土星形等离子球。",
    "プラズマボールの移動速度は遅いが、強力な追尾性能を有する。": "等离子球移动速度慢，但拥有强力追踪性能。",
    "充填することにより複数のボールを射出可能。": "通过充填可射出多个球体。",
    "超高熱の炎を噴射し、近〜中距離の敵に熱攻撃を加える。": "喷射超高热火焰，对近至中距离敌人施加热攻击。",
    "チェーンを射出し、捕えた敵を自分の目の前に引き寄せる。": "射出锁链，将捕捉的敌人拉到自己面前。",
    "引き寄せた敵をスタン状態にすることがある。": "有时可使拉近的敌人进入眩晕状态。",
    "引き寄せた敵を浮かし状態にすることがある。": "有时可使拉近的敌人进入挑空状态。",
    "ロックオンした敵に向かって炎の道を作り出す。": "向锁定敌人制造火焰之路。",
    "炎の道は一定時間経つと消滅する。": "火焰之路会在一定时间后消失。",
    "複数の出力ユニットからを射出されるレーザーを収束させて": "将多个输出单元射出的激光收束，",
    "連続照射する強力なレーザー砲。": "形成可连续照射的强力激光炮。",
    "大量の高エネルギー粒子を一点に向かって射出するビーム兵器。": "向一点射出大量高能粒子的光束兵器。",
    "非常に扱いやすく、射出中でも移動速度は低下しない。": "非常易于操作，射出中移动速度也不会降低。",
    "攻撃ボタンを押しつづけることで2連射が可能。": "按住攻击键可进行二连射。",
    "出力が強化され、大型のビームを射出する。": "输出得到强化，可射出大型光束。",
    "出力が強化され、より高速にビームを射出する。": "输出得到强化，可更高速射出光束。",
    "ロックオンした敵を自動追尾するプラズマビームを3本射出する。": "射出三道会自动追踪锁定敌人的等离子光束。",
    "火力、命中率、弾数など全てがハイレベルな実用性の高い武装。": "火力、命中率、弹数等均属高水准，实用性很高。",
    "ロックオンした敵を自動追尾する重イオンビームを3本射出する。": "射出三道会自动追踪锁定敌人的重离子光束。",
    "ロックオンした敵を自動追尾するプラズマビームを多数射出する。": "大量射出会自动追踪锁定敌人的等离子光束。",
    "攻撃ボタンを押しつづけることによって射出弾数が増える。": "按住攻击键可增加射出弹数。",
    "ロックオンした敵を自動追尾する重イオンビームを多数射出する。": "大量射出会自动追踪锁定敌人的重离子光束。",
    "未実装": "未实装",
    "伝説の爆破技師をモチーフにした特殊武装。": "以传说爆破技师为原型的特殊武装。",
    "デウカリオーンの武装供給プログラムのバグにより": "据说因丢卡利翁武装供给程序的错误，",
    "この武装は作られたと言われる。": "才生成了这种武装。",
    "ロックオンした敵への命中補正機能付き電磁ボールを射出する。": "射出带有锁定敌人命中补正功能的电磁球。",
    "電磁ボールに触れた敵はスタン状態になる。": "接触电磁球的敌人会进入眩晕状态。",
    "ロックオンした敵を自動追尾する電磁ボールを射出する。": "射出会自动追踪锁定敌人的电磁球。",
    "AIセルの形状を防御に特化させたシールド。": "将AI细胞形态特化为防御的盾牌。",
    "物理攻撃によるダメージを軽滅する。": "减轻物理攻击造成的伤害。",
    "ガード実行中は物理、電子ダメージを完全に無効化する。": "防御中完全无效化物理与电子伤害。",
    "ガード実行時の移動速度低下が少ない。": "防御时移动速度下降较少。",
    "ガード実行時の移動速度低下が無い。": "防御时移动速度不会下降。",
    "物理攻撃によるダメージ軽滅に加え、耐熱効果も備える。": "除减轻物理伤害外，还具备耐热效果。",
    "攻撃が命中する直前に局所的な電磁フィールドを発生させ、": "在攻击命中前瞬间产生局部电磁场，",
    "反発力により物理、電子攻撃によるダメージを軽滅するシールド。": "以斥力减轻物理与电子攻击伤害的盾牌。",
    "AIセルの相互干渉現象を利用し、反射レベルの反応速度で": "利用AI细胞相互干涉现象，以反射级反应速度",
    "衝撃拡散を実現したシールド。": "实现冲击扩散的盾牌。",
    "フラクタルシールドの強化版で、物理攻撃によるダメージを": "作为分形盾的强化版，可将物理攻击伤害",
    "大きく軽滅する。": "大幅减轻。",
    "プラズマソードの原理を応用し、板状にプラズマを放出することで": "应用等离子剑原理，通过板状释放等离子，",
    "あらゆる攻撃を「焼き防ぐ」効果を持つ盾。": "拥有“烧灼防御”所有攻击效果的盾牌。",
    "ただし、莫大なエネルギーを必要とする。": "但需要庞大能量。",
    "鏡面状のシールドで、レーザー系のダメージを軽滅する。": "镜面状盾牌，可减轻激光系伤害。",
    "物理攻撃に対しての防御効果は低い。": "对物理攻击的防御效果较低。",
    "与えられた衝撃を全身を使って受け流す機構を持ち、": "具备以全身卸开所受冲击的机构，",
    "物理スタン、叩きつけ、ノックバック状態になりにくくする。": "使物理眩晕、砸倒、击退状态更难发生。",
    "電子妨害装置。": "电子干扰装置。",
    "使用すると一定時間敵からロックオンされなくなる。": "使用后一定时间内不会被敌人锁定。",
    "使用すると一定時間背景に溶け入み、光学認識を妨げる。": "使用后一定时间内融入背景，妨碍光学识别。",
    "光学認識のみの問題で、レーダーには反応する。": "只影响光学识别，雷达仍会反应。",
    "使用するとオーバードライブ状態を発動させる究極のユニット。": "使用后发动超限驱动状态的究极单元。",
    "製作者は不明で、動作原理すら解明されていない。": "制作者不明，连运作原理也尚未解析。",
    "使用すると一定時間、移動速度が速くなる。": "使用后一定时间内移动速度提高。",
    "ロックオンした敵に一瞬で接近する。": "瞬间接近锁定的敌人。",
    "AIセルの形状を防御に特化させたアーマー。": "将AI细胞形态特化为防御的装甲。",
    "反発力により物理、電子攻撃によるダメージを軽滅するアーマー。": "以斥力减轻物理与电子攻击伤害的装甲。",
    "あらゆる攻撃を「焼き防ぐ」効果を持つアーマー。": "拥有“烧灼防御”所有攻击效果的装甲。",
    "鏡面状のアーマーで、レーザー系のダメージを軽滅する。": "镜面状装甲，可减轻激光系伤害。",
    "素体の脚": "素体腿部。",
    "エネルギーパックと弾倉を追加搭載する脚部パーツ。": "追加搭载能量包与弹匣的腿部部件。",
    "装備中の武装のエネルギーまたは弾倉を使い切った時、": "当装备中的武装用尽能量或弹匣时，",
    "自動的にその武装を完全補給する。": "自动为该武装完全补给。",
    "装備をエネルギー切れにする（ブレイクダウン）攻撃を": "对使装备能量耗尽（Breakdown）的攻击，",
    "50%の確率で無効化する。": "以50%概率无效化。",
    "65%の確率で無効化する。": "以65%概率无效化。",
    "80%の確率で無効化する。": "以80%概率无效化。",
    "ほぼ無効化する。": "几乎完全无效化。",
    "緊急回避時、サイドステップする。": "紧急回避时会侧步。",
    "通常の脚部パーツに比べ、移動速度を 20%上昇させる。": "相比普通腿部部件，移动速度提高20%。",
    "冷却にエネルギーを使用するため、温度上昇には注意が必要。": "因会用能量进行冷却，需要注意温度上升。",
    "移動速度低下（スロウ）状態になりにくい。": "较不容易进入移动速度下降（Slow）状态。",
    "通常の脚部パーツに比べ、移動速度を 30%上昇させる。": "相比普通腿部部件，移动速度提高30%。",
    "通常の脚部パーツに比べ、移動速度を 40%上昇させる。": "相比普通腿部部件，移动速度提高40%。",
    "超低温の液体化合物を用いた、液体冷式の冷却装置。": "使用超低温液体化合物的液冷式冷却装置。",
    "オーバーヒートを防ぎ、重火器の連続使用を可能にする。": "防止过热，使重火器可连续使用。",
    "冷却セルを用いた、昇華式の冷却装置。": "使用冷却细胞的升华式冷却装置。",
    "自己修復システムを搭載し、耐久力の自己修復を促進する。": "搭载自我修复系统，促进耐久力自我修复。",
    "クリティカル攻撃を40%の確率で無効化する。": "以40%概率无效化暴击攻击。",
    "クリティカル攻撃を55%の確率で無効化する。": "以55%概率无效化暴击攻击。",
    "クリティカル攻撃を70%の確率で無効化する。": "以70%概率无效化暴击攻击。",
    "クリティカル攻撃を85%の確率で無効化する。": "以85%概率无效化暴击攻击。",
    "全身の表面に光線を拡散させる粒子を発生させ、": "在全身表面产生扩散光线的粒子，",
    "レーザー系武装によるダメージのほとんどを無効化する。": "几乎无效化激光系武装造成的伤害。",
    "AIセルのオーバークロック機構を搭載し、機動性の向上を狙ったが": "搭载AI细胞超频机构，本意是提高机动性，",
    "動作が安定せずに失敗。": "但因运作不稳定而失败。",
    "しかし、オーバーヒート時にオーバードライブが発動するという": "不过，它产生了过热时会发动超限驱动的",
    "副作用があり、そこを実用化した偶発的な特殊武装。": "副作用，并将其作为偶发特殊武装实用化。",
    "尻尾のようなジャイロバランサーで衝撃を緩和し": "以尾巴般的陀螺平衡器缓和冲击，",
    "物理スタン状態にならなくする。": "使自身不会进入物理眩晕状态。",
    "ノックバック、吹き飛ばし状態にもならない。": "也不会进入击退、吹飞状态。",
    "ノックバック、吹き飛ばし、浮かし、叩きつけ状態にもならない。": "也不会进入击退、吹飞、挑空、砸倒状态。",
    "移動だけでなく攻撃を可能にした脚部武装。": "不仅能移动，也可攻击的腿部武装。",
    "敵をロックオンした状態で緊急回避を行うと": "在锁定敌人的状态下进行紧急回避时，",
    "ロックオンした敵に向かってキック攻撃を繰り出す。": "会朝锁定敌人发动踢击。",
    "イベント用": "事件用。",
    "なし": "无。",
}



ASCII_TO_FULLWIDTH = {
    **{chr(ord("0") + index): chr(ord("０") + index) for index in range(10)},
    **{chr(ord("A") + index): chr(ord("Ａ") + index) for index in range(26)},
    **{chr(ord("a") + index): chr(ord("ａ") + index) for index in range(26)},
}
FULLWIDTH_SOURCE_CODES = {
    **{chr(ord("０") + index): 0x0193 + index for index in range(10)},
    **{chr(ord("Ａ") + index): 0x019D + index for index in range(26)},
    **{chr(ord("ａ") + index): 0x01B7 + index for index in range(26)},
}

COMPRESSION_REPLACEMENTS = (
    ("近战用", "近战"),
    ("武装", "武器"),
    ("敌人", "敌"),
    ("敌方", "敌"),
    ("攻击", "攻"),
    ("伤害", "伤"),
    ("移动速度", "移速"),
    ("连续射击", "连射"),
    ("连续使用", "连用"),
    ("能量耗尽", "断能"),
    ("无效化", "无效"),
    ("一定时间内", "一段时间"),
    ("发动", "触发"),
    ("提高", "提升"),
    ("降低", "下降"),
    ("概率", "几率"),
    ("超限驱动", "超驱动"),
    ("等离子", "等离子"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build JP-first layered DATA001/0015 equipment sheets.")
    parser.add_argument("--review", type=Path, default=Path("local/work/translation_review_slim_v5/equipment.json"))
    parser.add_argument(
        "--source-sheet",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v35_quality/DATA001_0015_full_current_target_sheet.json"),
    )
    parser.add_argument(
        "--source-export",
        type=Path,
        default=Path("local/work/extract_text_DATA001_0015_seeded.json"),
        help="Source extraction with original glyph codes; used to preserve fullwidth Latin/digits only where the JP source uses them.",
    )
    parser.add_argument("--layer-root", type=Path, default=Path("local/work/translation_refine_v1/equipment_jp_layers_v2_reviewed"))
    parser.add_argument(
        "--target-root",
        type=Path,
        default=Path("local/work/translation_refine_v1/merged_target_sheets_v39_equipment_reviewed"),
    )
    parser.add_argument("--review-root", type=Path, default=Path("local/work/translation_review_slim_v9_equipment_reviewed"))
    parser.add_argument(
        "--reviewed",
        type=Path,
        default=Path("translation_reviewed/equipment.json"),
        help="Optional human-reviewed equipment pack. current_chs values override generated JP-first text.",
    )
    args = parser.parse_args()

    build_layers(args.review, args.source_sheet, args.source_export, args.layer_root, args.target_root, args.review_root, args.reviewed)
    return 0


def build_layers(
    review_path: Path,
    source_sheet_path: Path,
    source_export_path: Path,
    layer_root: Path,
    target_root: Path,
    review_root: Path,
    reviewed_path: Path | None = None,
) -> None:
    review_rows = json.loads(review_path.read_text(encoding="utf-8"))
    if reviewed_path is not None and reviewed_path.exists():
        review_rows = json.loads(reviewed_path.read_text(encoding="utf-8"))
    source_rows = json.loads(source_sheet_path.read_text(encoding="utf-8"))["entries"]
    source_by_key = {(int(row["record"]), int(row["run"])): row for row in source_rows}
    source_export_rows = json.loads(source_export_path.read_text(encoding="utf-8"))["entries"]
    source_codes_by_key = {
        (int(row["record"]), int(row["run"])): normalize_source_codes(row.get("codes", []))
        for row in source_export_rows
    }

    layer_entries: list[dict[str, Any]] = []
    target_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    unknown_clauses: set[str] = set()

    for row in review_rows:
        record, run = parse_review_id(str(row["id"]))
        source_row = source_by_key[(record, run)]
        max_units = int(source_row["source_max_units"])
        jp = str(row.get("jp", ""))
        en = str(row.get("en", ""))
        source_codes = source_codes_by_key.get((record, run), [])
        current = preserve_source_symbols(str(row.get("current_chs", row.get("chs", ""))), jp, source_codes)
        has_human_review = "current_chs" in row

        if run == 0:
            unshrunk = current
            shrink, name_fit = shrink_name_to_fit(current, max_units)
            fit_note = ("name_reviewed" if has_human_review else "name_current") if name_fit == "fits" else f"name_{name_fit}"
        elif has_human_review and current:
            unshrunk = current
            shrink, fit_note = shrink_to_fit(unshrunk, max_units, current)
            fit_note = f"reviewed_{fit_note}"
        else:
            unshrunk, row_unknowns = translate_equipment_description(jp, current)
            unknown_clauses.update(row_unknowns)
            shrink, fit_note = shrink_to_fit(unshrunk, max_units, current)

        layer_entry = {
            "table": "DATA001/0015",
            "record": record,
            "run": run,
            "category": "equipment",
            "source_max_units": max_units,
            "jp": jp,
            "en": en,
            "current_chs": current,
            "chs_unshrunk": unshrunk,
            "chs_shrunk": shrink,
            "fit_note": fit_note,
        }
        layer_entries.append(layer_entry)
        target_entries.append(
            {
                "table": "DATA001/0015",
                "record": record,
                "run": run,
                "chs_draft": shrink,
                "source_max_units": max_units,
                "source": "translation_refine_v1/equipment_jp_layers_v2_reviewed",
                "notes": f"v39 reviewer equipment layered; fit={fit_note}",
            }
        )
        review_entries.append(
            {
                "id": f"DATA001/0015#{record:04d}:{run}",
                "category": "equipment",
                "jp": jp,
                "en": en,
                "current_chs": current,
                "chs_unshrunk": unshrunk,
                "chs_shrunk": shrink,
                "max_units": max_units,
                "fit_note": fit_note,
            }
        )

    layer_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    review_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "DATA001_0015_equipment_jp_layers.json").write_text(
        json.dumps({"entries": layer_entries}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (target_root / "DATA001_0015_full_current_target_sheet.json").write_text(
        json.dumps({"entries": target_entries}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (review_root / "equipment.json").write_text(
        json.dumps(review_entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {
        "rows": len(layer_entries),
        "description_rows": sum(1 for row in layer_entries if row["run"] == 1),
        "unknown_clauses": sorted(unknown_clauses),
        "fit_counts": fit_counts(layer_entries),
    }
    (layer_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def parse_review_id(text: str) -> tuple[int, int]:
    _table, rest = text.split("#", 1)
    record, run = rest.split(":", 1)
    return int(record), int(run)


def preserve_source_symbols(text: str, jp: str, source_codes: list[int]) -> str:
    result = text
    source_code_set = set(source_codes)
    if "㎜" in jp or 0x03B6 in source_code_set:
        result = result.replace("mm", "㎜")
    if "Ⅴ" in jp or 0x032A in source_code_set:
        result = result.replace("V", "Ⅴ")
    return apply_source_fullwidth_latin(result, source_code_set)


def normalize_source_codes(raw_codes: Any) -> list[int]:
    if not isinstance(raw_codes, list):
        return []
    codes: list[int] = []
    for code in raw_codes:
        try:
            codes.append(int(code, 16 if isinstance(code, str) and code.lower().startswith("0x") else 10))
        except (TypeError, ValueError):
            continue
    return codes


def apply_source_fullwidth_latin(text: str, source_code_set: set[int]) -> str:
    chars: list[str] = []
    for char in text:
        fullwidth = ASCII_TO_FULLWIDTH.get(char)
        if fullwidth is not None and FULLWIDTH_SOURCE_CODES[fullwidth] in source_code_set:
            chars.append(fullwidth)
        else:
            chars.append(char)
    return "".join(chars)


def translate_equipment_description(jp: str, current: str) -> tuple[str, set[str]]:
    normalized = jp.replace("＊", "*").replace("　", "").strip()
    if not normalized:
        return current, set()
    boss = translate_boss_label(normalized)
    if boss is not None:
        return boss, set()
    unknowns: set[str] = set()
    translated: list[str] = []
    for clause in normalized.split("*"):
        clause = clause.strip()
        if not clause:
            continue
        boss_clause = translate_boss_label(clause)
        if boss_clause is not None:
            translated.append(boss_clause)
            continue
        chs = CLAUSE_TRANSLATIONS.get(clause)
        if chs is None:
            unknowns.add(clause)
            chs = current
        translated.append(chs)
    return "\n".join(translated), unknowns


def translate_boss_label(text: str) -> str | None:
    compact = text.replace(" ", "").replace("　", "")
    match = re.fullmatch(r"(\d+)Fボス(.+?)(頭|右腕|左腕|右手|胸|脚)", compact)
    if not match:
        return None
    floor, boss, part = match.groups()
    boss_name = BOSS_NAMES.get(boss, boss)
    part_name = PART_NAMES.get(part, part)
    return f"{floor}F Boss {boss_name} {part_name}"


def shrink_name_to_fit(text: str, max_units: int) -> tuple[str, str]:
    normalized = normalize_punctuation(text)
    if code_units(normalized) <= max_units:
        return normalized, "fits"
    replacements = (
        ("重型榴弹炮", "重榴弹炮"),
        ("反装甲", "反甲"),
        ("重型", "重"),
    )
    candidate = normalized
    for source, target in replacements:
        candidate = candidate.replace(source, target)
    if code_units(candidate) <= max_units:
        return candidate, "reviewed_compressed"
    return hard_trim(candidate, max_units), "reviewed_hard_trimmed"


def shrink_to_fit(text: str, max_units: int, current: str) -> tuple[str, str]:
    normalized = normalize_punctuation(text)
    if code_units(normalized) <= max_units:
        return normalized, "unshrunk_fits"

    boss_candidate = compact_boss_label(normalized)
    if boss_candidate != normalized and code_units(boss_candidate) <= max_units:
        return boss_candidate, "compact_boss_label"

    candidate = normalized
    for source, target in COMPRESSION_REPLACEMENTS:
        candidate = candidate.replace(source, target)
    candidate = compact_lines(candidate)
    if code_units(candidate) <= max_units:
        return candidate, "compressed"

    current_normalized = normalize_punctuation(current)
    if current_normalized and current_normalized != "0" and code_units(current_normalized) <= max_units:
        return current_normalized, "fallback_current_fit"

    trimmed = hard_trim(candidate, max_units)
    return trimmed, "hard_trimmed"


def normalize_punctuation(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def compact_lines(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def compact_boss_label(text: str) -> str:
    match = re.fullmatch(r"(\d+F) Boss (.+) (头部|右臂|左臂|右手|胸部|腿部)", text)
    if not match:
        return text
    floor, boss, part = match.groups()
    short_part = {"头部": "头", "胸部": "胸", "腿部": "腿"}.get(part, part)
    return f"{floor}{boss}{short_part}"


def hard_trim(text: str, max_units: int) -> str:
    text = text.replace("\n", " ")
    if len(text) <= max_units:
        return text
    trimmed = text[:max_units].rstrip("，。、；： ")
    return trimmed or text[:max_units]


def code_units(text: str) -> int:
    return len(text)


def fit_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        note = str(entry["fit_note"])
        counts[note] = counts.get(note, 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
