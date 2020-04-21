import os

from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from helpers.paths import benchmarks_path

# from https://xkcd.com/color/rgb/
tool_colors = {
    "Logstash": "xkcd:sky",
    "Wolf": "xkcd:salmon",
    "Netcat": "xkcd:green",
    "Libraries": "xkcd:red",
    "Wolf with json\nconversion": "xkcd:peach"
}

tool_order = [
    "Logstash",
    "Netcat",
    "Wolf",
    "Wolf with json\nconversion",
    "Libraries"
]

units_order = [
    "s",
    "%",
    "msg/s",
    "µs/msg",
    "MB",
    "B/msg",
    "GB",
]

mes_order = [
    "Tool's size",
    "Linux docker image size",
]

left_title = {
    "Wolf compilation": 1.9,
    "Disk usage": 2.5,
    "Empty compilation": 1.9,
'Empty configuration no input': 1.8,
'Empty configuration trickle': 1.5,
'Empty configuration full load': 1.5,
'Empty configuration buffer then read': 1.5,
'Collector compilation': 1.9,
'Collector no input': 1.85,
'Collector trickle': 1.7,
'Collector full load': 1.7,
'Parser trickle': 1.65,
'Parser full load': 1.6,
}


def render_result(name, *measurements):
    res = {}
    for m in measurements:
        res.update(m)
    tools = list(set([g for g in res.keys()]))
    measurements = list(set([(m, res[g][m][1]) for g in res.keys() for m in res[g].keys()]))
    units = {}
    for measurement, unit in measurements:
        if unit not in units: units[unit] = {}
        store = units[unit]

        for tool in tools:
            if measurement not in store: store[measurement] = {}
            if measurement in res[tool] and unit == res[tool][measurement][1]:
                store[measurement][tool] = res[tool][measurement]

    subplots = len(units)
    unit_keys = sorted(units.keys(), key=lambda x: units_order.index(x))
    print(unit_keys)
    width_ratios = [sum([len(units[u][m]) for m in units[u]]) + (len(units[u]) - 1) for u in unit_keys]
    _, subplots = plt.subplots(1, subplots, gridspec_kw={'width_ratios': width_ratios},
                               figsize=(sum(width_ratios) / 2 + 2, 5))
    if len(units) == 1:
        subplots = [subplots]

    for u, unit in enumerate(unit_keys):
        measurements = units[unit]
        width = 1

        ax = subplots[u]
        mx_value = 0
        mn_value = pow(10, 100)
        spacing = 0.02

        def auto_label(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                s = f"{int(height)}"
                extra = ""
                if height == 0:
                    pass
                elif height == 0.000001:
                    s = ''
                elif height < 10:
                    s = f'{height:.2f}'
                elif height < 100:
                    s = f'{height:.1f}'
                elif height >= 1000 and height < 10000:
                    s = f'{height / 1000:.1f}'
                    extra = "k"
                elif height >= 10000:
                    s = f'{int(height / 1000)}'
                    extra = "k"
                while "." in s and s.endswith("0"):
                    s = s[:-1]
                    if s.endswith("."):
                        s = s[:-1]
                s += extra
                ax.annotate(s,
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 0),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',
                            fontsize="x-small",
                            color="grey",
                            bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'),
                            zorder=10)

        brs = []
        i = 0
        xticks = []
        def get_mes_pos(x):
            try:
                return mes_order.index(x)
            except ValueError:
                print(x)
                return x
        for measurement in sorted(measurements, key=get_mes_pos):
            group = measurements[measurement]
            xticks.append(i * width + width * len(group) / 2 - width / 2 + spacing)
            for tool in sorted(tools, key=lambda x: tool_order.index(x)):
                try:
                    value = max(group[tool][0], 0)
                    brs.append((width * i + spacing, value, tool))
                    mx_value = max(mx_value, value)
                    mn_value = min(mn_value, value)
                    i += 1
                except KeyError:
                    brs.append((0, 0.000001, tool))
            i += 1

        bars = {}

        for r, v, t in brs:
            if t not in bars: bars[t] = {"r": [], "v": []}
            bars[t]["r"].append(r)
            bars[t]["v"].append(v)

        for t in bars:
            r, v = bars[t]["r"], bars[t]["v"]
            auto_label(ax.bar(r, v, width=width - spacing * 2, label=t, zorder=100, linewidth=0,
                              color=[tool_colors[t] for _ in range(len(r))]))

        ax.set_title(f"[{unit}]   ", position=(0, 1), fontweight='ultralight', ha="right", fontsize="small", alpha=0.5,
                     stretch=0)
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('left')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        ax.yaxis.set_tick_params(labelcolor="grey", color="lightgrey")
        ax.ticklabel_format(style='plain')

        def plain(x, pos):
            if x >= 1:
                return str(int(x))
            return str(x)

        # if mn_value * 100 < mx_value:
        #     ax.set_yscale('log')
        #     ax.yaxis.set_major_formatter(FuncFormatter(plain))
        ax.set_xticks(xticks)
        ax.set_xticklabels([s.replace(" ", "\n") for s in sorted(measurements, key=get_mes_pos)])

        ax.yaxis.grid(which="major", color='lightgrey', zorder=0)
        ax.set_yticks(ax.get_yticks()[1:-1])
        if len(ax.get_yticks()) > 0 and ax.get_yticks()[-1] > mx_value:
            ax.set_yticks(ax.get_yticks()[:-1])

        def millions(x, pos):
            return f'{x / 1000:1.0f}k'

        if unit.startswith("msg") and ax.get_yticks()[0] > 1000:
            formatter = FuncFormatter(millions)
            ax.yaxis.set_major_formatter(formatter)

        if u + 1 == len(unit_keys):

            plt.text(left_title[name], 0, name.replace(" ", "\n") + "\n\n", ha="left", va="bottom", transform=ax.transAxes,
                     ma="left",
                     size="x-large", fontstyle="italic", fontfamily="serif")
        # plt.setp(ax.get_yticklabels()[0], visible=False)
        # plt.setp(ax.get_yticks(), visible=False)
        # plt.setp(ax.get_yticklabels()[-1], visible=False)

    right_spacing = sum(width_ratios) / (sum(width_ratios) + 3) - 0.08
    wspace = (len(units) + 1) / len(units)
    print(wspace)
    plt.subplots_adjust(right=right_spacing, left=min(0.15 - sum(width_ratios)/400, right_spacing-0.01), bottom=0.2, wspace=wspace - 0.5)
    # plt.tight_layout(w_pad=1)

    if len(tools) > 1:
        subplots[-1].legend(loc='upper left', edgecolor="none", facecolor="none", bbox_to_anchor=(wspace*2-1, 1))

    if not os.path.exists(benchmarks_path):
        os.mkdir(benchmarks_path)

    # Update the plot
    plt.savefig(os.path.join(benchmarks_path, f"{name}.png"), dpi=300)
