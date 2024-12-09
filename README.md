# FINAL-ORAL-REPORT
# 透過爬蟲蒐集美國職棒球員資料分析及預測勝場
# 使用工具及技術
### 1.Python selenium
### 2.MYSQL
### 3.回歸分析
### 4.Random Forest Regressor
### 5.Matplotlib
### 6.Panda
### 7.Git
## -----流程-----
### 1.蒐集有關球隊的資訊來自公開網站，例如:戰績，球員個人成績
### 2.設計多個程式爬取這些資料(使用selenium 用python來呈現)
### 3.將蒐集到的內容儲存在資料庫或以excel形式保存
### 4.對於欄位的資訊進行劃分，掌握那些欄位對於比賽勝利有幫助(要分析時優先挑選)
### 5.使用Random Forest Regressor 模型分析
### 6.利用其他模型比對內容是否吻合，接著預測勝場
## -----分割線-----
### 下面這張圖是Random Forest Regressor模型輸出做成的視覺化圖形
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/main/shap_summary_plot.png" alt="predict_scaater" width="700" >

## 以下是蒐集爬取球隊戰績程式碼
### 藉由selenium抓取資料以及弄成excel和存入MYSQL

[點擊這裡查看 HTML 文件](https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/main/PDF/mlb_history_standings.xlsx%20-%20Sheet2010.pdf)

<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖.png" alt="圖片_1" width="700" >
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖_2.png" alt="圖片_2" width="700" >
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖_3.png" alt="圖片_3" width="700" >
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖_4.png" alt="圖片_4" width="700" >
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖_5.png" alt="圖片_5" width="700" >
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖_6.png" alt="圖片_6" width="700" >
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖_7.png" alt="圖片_7" width="700" >
<img src="https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/dev/picture_code/截圖_8.png" alt="圖片_8" width="700" >

[點擊這裡查看 HTML 文件](https://github.com/zhengmichael061/FINAL-ORAL-REPORT/blob/main/force_plot.html)

