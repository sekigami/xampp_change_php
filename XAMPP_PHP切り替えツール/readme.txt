### XAMPP PHPバージョン切り替えツール ヘルプ ###

このツールを使用すると、XAMPPのPHP, Apacheの
バージョンを簡単に切り替えることができます。

【事前準備】
1. XAMPPのフォルダに以下のように各バージョンを配置してください。
   - C:\xampp\php7.4
   - C:\xampp\apache7.4
   - C:\xampp\php8.1
   - C:\xampp\apache8.1
   
   ※これ以外の形式には対応してませんので注意して下さい。

2. ツールを管理者権限で実行してください。
   - シンボリックリンクの変更には管理者権限が必要です。

【使用方法】
1. 「PHPのバージョンを選択」から切り替えたいバージョンを選ぶ。
2. 「切り替え」ボタンを押す。
3. Apacheが再起動し、指定したバージョンに切り替わります。
4. 「再読み込み」ボタンを押すと、xamppフォルダ内を再検索し、違うバージョンがあれば追加されます。

【注意】
- XAMPPが動作中の場合は、Apacheを停止してから切り替えてください。
- PHPのバージョンが切り替わった後、必要に応じてApacheを手動で再起動してください。
- phpMyAdmin の設定ファイル（config.inc.php）が
  バージョンによって異なる可能性があるため、適宜確認してください。

以上の準備を行えば、スムーズに切り替えを行えます！
