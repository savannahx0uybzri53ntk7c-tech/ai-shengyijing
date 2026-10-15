# 图示合同 v1

在此 Skill 根目录运行脚本，Python 3.10+，仅标准库。生成目标选新路径；脚本会覆盖同名输出，不能传入需要保留的用户原件。

支持 `architecture / flow / cycle / timeline / matrix / comparison` 六种关系。
风格支持 `ai-business / ai-business-wine-balanced / ai-business-gold-noir / ai-business-ivory-gold / ai-vitality / humanist`；输出形式为 `scroll / deck`，双模式各运行一遍。

最小输入见 [flow.json](../examples/flow.json)。节点 ID 唯一，边端点必须存在。flow/cycle 按 nodes 顺序布局；未传 edges 时脚本会自动串联，因此先确认语义确有顺序，非顺序关系用正确 type 并显式给边。timeline 可含 time，matrix 节点 x/y 为0—1，comparison 用 group 分列且最多三组。

```sh
python3 scripts/diagram_compiler.py examples/flow.json --check-only
python3 scripts/diagram_compiler.py examples/flow.json --style humanist --form scroll --output diagram.html
```

输出是含内联 SVG 的 figure 片段，不是完整网页。scroll 内含桌面与手机两种 SVG；嵌入最终页时加以下显隐样式，并为 SVG 设置宽度，不把两版一起显示：

```css
.ha-diagram-figure { margin: 0; }
.ha-diagram-figure svg { display: block; width: 100%; height: auto; }
.ha-diagram-mobile-wrap { display: none; }
@media (max-width: 600px) {
  .ha-diagram-desktop-wrap { display: none; }
  .ha-diagram-mobile-wrap { display: block; }
}
```

节点标题宜短，最多两个焦点。超过九节点优先拆图；边只表达一项关系，多种箭头含义要有图例。source_node_count 超过实际节点数时，fidelity_ledger.notes 说明归并内容，不能静默删事实。

SVG 保留非空 title/desc、唯一前缀 ID、role 与 aria-labelledby。图示输入校验只证明格式可接受，编译成功只证明生成片段；完整页面仍需真实桌面和手机截图检查语义、字体、线条、遮挡与可读性。不能将 JSON PASS 当视觉或业务质量验收。
