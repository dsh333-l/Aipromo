export interface WindowModel {
  id: string;
  name: string;
  windowType: string;
  material: string;
  aluminum: string;
  coating: string;
  opening: string;
  glass: string;
  hardware: string;
  handle: string;
  screen: string;
  seal: string;
  paint: string;
  colorWood: string;
  colorAluminum: string;
  drainage: string;
  cornerGuard: string;
  glassRailing: string;
  waterTightness: string;
  airTightness: string;
  pressureResistance: string;
  insulation: string;
  soundInsulation: string;
  visibleWidth: string;
  keywords: string[];
}

export const WINDOW_MODELS: WindowModel[] = [
  {
    id: "AT77",
    name: "AT77铝合金内开窗（东方甄选系列）",
    windowType: "内开窗",
    material: "/",
    aluminum: "高精级硅镁铝合金",
    coating: "DX6000纳米级环保喷涂",
    opening: "内开内倒",
    glass: "标配玻璃厚度规格29/39mm，可升级6净功能或5G中空系统",
    hardware: "德国ROTO T480五金",
    handle: "不锈钢无底座执手",
    screen: "标配可拆卸一体纱窗（标配0.35mm金刚网）纱扇配置弹出式带锁执手",
    seal: "开启三道EPDM密封，室外侧玻璃胶条为遇水膨胀胶条",
    paint: "无醛水性漆",
    colorWood: "/",
    colorAluminum: "多种颜色支持定制",
    drainage: "隐藏式排水",
    cornerGuard: "圆弧角部护角（黑色）",
    glassRailing: "落地窗可选装玻璃护栏（6+0.76pvb+6夹胶安全玻璃）",
    waterTightness: "4",
    airTightness: "7",
    pressureResistance: "7",
    insulation: "≤2.74",
    soundInsulation: "34dB",
    visibleWidth: "单固定（55）；单开启（87.2）；一开一固（111）；中榳宽度（80）",
    keywords: ["铝合金内开窗", "高精级硅镁铝合金", "DX6000环保喷涂", "德国ROTO五金", "隐藏式排水"],
  },
  {
    id: "AT87",
    name: "AT87内开窗框扇齐平（阿鲁曼系列）",
    windowType: "内开窗",
    material: "/",
    aluminum: "高精级硅镁铝合金",
    coating: "DX6000纳米级环保喷涂",
    opening: "内开内倒",
    glass: "玻璃厚度规格29/39mm，可升级6净功能或5G中空系统",
    hardware: "德国ROTO外开窗五金",
    handle: "系统定制不锈钢有底座执手",
    screen: "/",
    seal: "开启三道EPDM密封，室外侧玻璃胶条为遇水膨胀胶条",
    paint: "无醛水性漆",
    colorWood: "/",
    colorAluminum: "多种颜色支持定制",
    drainage: "/",
    cornerGuard: "/",
    glassRailing: "落地窗可选装玻璃护栏（6+0.76pvb+6夹胶安全玻璃）",
    waterTightness: "4",
    airTightness: "7",
    pressureResistance: "7",
    insulation: "≤2.74",
    soundInsulation: "34dB",
    visibleWidth: "单固定（55）；单开启（87.2）；一开一固（111）；中榳宽度（80）",
    keywords: ["齐平内开窗", "阿鲁曼系列", "高精级硅镁铝合金", "DX6000环保喷涂", "德国ROTO五金"],
  },
  {
  id: "AR120",
  name: "AR120外开窗纱一体（阿鲁曼系列）",
  windowType: "外开窗",
  material: "/",
  aluminum: "高精级硅镁铝合金",
  coating: "DX6000纳米级环保喷涂",
  opening: "外开",
  glass: "玻璃厚度规格29/39mm,可升级6净功能或5G中空系统",
  hardware: "德国ROTO窗纱一体五金",
  handle: "系统定制不锈钢有底座执手",
  screen: "标配内开磁吸可拆卸一体纱窗(标配0.35mm金刚网)",
  seal: "开启三道EPDM密封，室外侧玻璃胶条为遇水膨胀胶条",
  paint: "无醛水性漆",
  colorWood: "/",
  colorAluminum: "多种颜色支持定制",
  drainage: "/",
  cornerGuard: "/",
  glassRailing: "落地窗可选装玻璃护栏（6+0.76pvb+6夹胶安全玻璃）",
  waterTightness: "4",
  airTightness: "6",
  pressureResistance: "9",
  insulation: "≤3.05",
  soundInsulation: "33dB",
  visibleWidth: "单固定（48.5）；单开启（131.3）；一开一固（148.8）；中梃宽度（66）",
  keywords: ["外开窗纱一体", "阿鲁曼系列", "高精级硅镁铝合金", "DX6000环保喷涂", "德国ROTO窗纱一体五金"],
},
];
