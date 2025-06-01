namespace SleepyWinform
{
    partial class SleepyWinform
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(SleepyWinform));
            this.configview = new System.Windows.Forms.Button();
            this.listView1 = new System.Windows.Forms.ListView();
            this.time = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.logcontent = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.SuspendLayout();
            // 
            // configview
            // 
            this.configview.Location = new System.Drawing.Point(995, 58);
            this.configview.Margin = new System.Windows.Forms.Padding(4);
            this.configview.Name = "configview";
            this.configview.Size = new System.Drawing.Size(112, 34);
            this.configview.TabIndex = 1;
            this.configview.Text = "配置";
            this.configview.UseVisualStyleBackColor = true;
            this.configview.Click += new System.EventHandler(this.button1_Click);
            // 
            // listView1
            // 
            this.listView1.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.time,
            this.logcontent});
            this.listView1.HideSelection = false;
            this.listView1.Location = new System.Drawing.Point(67, 221);
            this.listView1.Name = "listView1";
            this.listView1.Size = new System.Drawing.Size(1062, 319);
            this.listView1.TabIndex = 4;
            this.listView1.UseCompatibleStateImageBehavior = false;
            this.listView1.View = System.Windows.Forms.View.Details;
            // 
            // time
            // 
            this.time.Text = "时间";
            this.time.Width = 121;
            // 
            // logcontent
            // 
            this.logcontent.Text = "日志内容";
            this.logcontent.Width = 461;
            // 
            // sleepy_winform
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 18F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1200, 675);
            this.Controls.Add(this.listView1);
            this.Controls.Add(this.configview);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Margin = new System.Windows.Forms.Padding(4);
            this.Name = "sleepy_winform";
            this.Opacity = 0.9D;
            this.Text = "sleepy_winform";
            this.FormClosed += new System.Windows.Forms.FormClosedEventHandler(this.Form1_FormClosed);
            this.Load += new System.EventHandler(this.Form1_Load);
            this.ResumeLayout(false);

        }

        #endregion
        private System.Windows.Forms.Button configview;
        private System.Windows.Forms.ListView listView1;
        private System.Windows.Forms.ColumnHeader time;
        private System.Windows.Forms.ColumnHeader logcontent;
    }
}

