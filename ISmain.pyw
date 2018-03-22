import wx
import wx.lib.scrolledpanel
import os
import locale
import urllib.request
import imagescraper

locale.setlocale(locale.LC_ALL, 'C')

# Gauge Panel Class to display progress of editing images #
class StatusGauge(wx.Panel):
    def __init__(self, parent, TotalItems, Operation):
        wx.Panel.__init__(self, parent)

        self.Gauge = wx.Gauge(self, wx.ID_ANY, TotalItems)
        self.Gauge.Pulse()
        self.Info = wx.StaticText(self, wx.ID_ANY, Operation)
        self.Percent = wx.StaticText(self, wx.ID_ANY, '0 %')

        self.HSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)

        self.HSizer.Add(self.Gauge, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        self.HSizer.Add(self.Percent, 0, wx.ALL, 5)

        self.Sizer.Add(self.Info, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        self.Sizer.Add(self.HSizer, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(self.Sizer)
        self.Fit()

    def ChangeGauge(self, Value):
        self.Gauge.SetValue(Value)

    def ChangeText(self, Text):
        self.HSizer.Hide(self.Percent)
        self.Percent.SetLabel(Text)
        self.HSizer.Show(self.Percent)
        
# Panel that displays four buttons                                            #
# Deselect All -> Unchecks all Image Combo Boxes                              #
# Select All -> Checks all Image Combo Boxes                                  #
# Confirm -> Saves the images that are checked in the Image Combo Boxes       #
# Cancel -> Cancels the download of images [Removes all images from computer] #
class ImageControls(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.frame = parent

        self.ImageDeselectAll = wx.Button(self, wx.ID_ANY, 'Deselect All')
        self.Bind(wx.EVT_BUTTON, self.Deselect, self.ImageDeselectAll)
        self.ImageSelectAll = wx.Button(self, wx.ID_ANY, 'Select All')
        self.Bind(wx.EVT_BUTTON, self.Select, self.ImageSelectAll)
        self.ConfirmSelected = wx.Button(self, wx.ID_ANY, 'Confirm')
        self.Bind(wx.EVT_BUTTON, self.Confirm, self.ConfirmSelected)
        self.CancelAll = wx.Button(self, wx.ID_ANY, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.Remove, self.CancelAll)
        
        self.ButtonHSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ButtonHSizer.Add((20,20), proportion=1)
        self.ButtonHSizer.Add(self.ImageDeselectAll, 0, wx.ALL|wx.CENTER, 5)
        self.ButtonHSizer.Add(self.ImageSelectAll, 0, wx.ALL|wx.CENTER, 5)
        self.ButtonHSizer.Add(self.ConfirmSelected, 0, wx.ALL|wx.CENTER, 5)
        self.ButtonHSizer.Add(self.CancelAll, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(self.ButtonHSizer)
        self.Fit()
            
    def Select(self, event):
        for box in self.frame.ImagePanel.Images: box.SetCheckStatus(True)

    def Deselect(self, event):
        for box in self.frame.ImagePanel.Images: box.SetCheckStatus(False)

    def Confirm(self, event):
        self.frame.DisableButtons()
        self.frame.CloseLock = True
        Check = [[box.GetImageName(), box.ImageName.GetValue()] for box in self.frame.ImagePanel.Images]
        if imagescraper.file_check(Check):       
            LoadingFrame = wx.Frame(None, wx.ID_ANY, 'Image Downloader')
            LoadingPanel = StatusGauge(LoadingFrame, 100, 'Handling Images ...')
            LoadingFrame.Center()
            LoadingFrame.Fit()
            LoadingFrame.Show()
            count = 0
            
            self.frame.Discontinue = False
            for box in self.frame.ImagePanel.Images:
                if box.GetCheckStatus(): imagescraper.rename_file(box.GetImageName(), box.ImageName.GetValue())                    
                else: imagescraper.remove_file(box.GetImageName())
                count+=1
                LoadingPanel.ChangeGauge((count/len(self.frame.ImagePanel.Images))*100)
                LoadingPanel.ChangeText(str(int(LoadingPanel.Gauge.GetValue()))+' %')
                wx.Yield()

            LoadingFrame.Destroy()
            self.frame.RemovePanels()
            self.frame.mainPanel.SetError('Selected Images were Successfully Downloaded', True)
            self.frame.mainPanel.PromptInput.SetValue('')
        else:
            self.frame.mainPanel.SetError("Error: Make Sure filenames have a Valid Extension at the end (ex: '.jpg', '.png')", False) 

        self.frame.EnableButtons()
        self.frame.VPanelSizer.Layout()
        self.frame.VPanelSizer.Fit(self.frame)
        self.frame.CloseLock = False

    def Remove(self, event):
        self.Cancel()
        self.frame.mainPanel.PromptInput.SetValue('')

    def Cancel(self):
        self.frame.DisableButtons()
        self.frame.CloseLock = True
        LoadingFrame = wx.Frame(None, wx.ID_ANY, 'Image Downloader')
        LoadingPanel = StatusGauge(LoadingFrame, 100, 'Removing Images ...')
        LoadingFrame.Center()
        LoadingFrame.Fit()
        LoadingFrame.Show()
        count = 0
        
        self.frame.Discontinue = False
        for box in self.frame.ImagePanel.Images:
            imagescraper.remove_file(box.GetImageName())
            count+=1
            LoadingPanel.ChangeGauge((count/len(self.frame.ImagePanel.Images))*100)
            LoadingPanel.ChangeText(str(int(LoadingPanel.Gauge.GetValue()))+' %')
            wx.Yield()

        LoadingFrame.Destroy()
        self.frame.EnableButtons()
        self.frame.RemovePanels()
        self.frame.mainPanel.SetError('', True)
        
        self.frame.VPanelSizer.Layout()
        self.frame.VPanelSizer.Fit(self.frame)
        self.frame.CloseLock = False

# A Scroll Panel Class that displays all Image Combo Boxes #
class ImageScrollPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, FileInfos):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(450,450))

        self.SetupScrolling()
        self.Sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.Images = [ImageCombo(self, img) for img in FileInfos]

        for img in self.Images: self.Sizer.Add(img, 0, wx.ALL|wx.EXPAND|wx.CENTER, 5)

        self.SetSizer(self.Sizer)
        self.Fit()

    def AddCombos(self, FileInfos):
        self.Images = [ImageCombo(self, img) for img in FileInfos]
        for img in self.Images: self.Sizer.Add(img, 0, wx.ALL|wx.EXPAND|wx.CENTER, 5)
        self.Layout()
        self.Fit()

    def RemoveCombos(self):
        while len(self.Sizer.GetChildren()) > 0:
            self.Sizer.Hide(len(self.Sizer.GetChildren())-1)
            self.Sizer.Remove(len(self.Sizer.GetChildren())-1)
            wx.Yield()
        self.Layout()
        self.Fit()
        
# Class of the Image Combo ; contains a Bitmap, checkbox, and a textctrl with the filename #
class ImageCombo(wx.Panel):
    def __init__(self, parent, ImageFile):
        wx.Panel.__init__(self, parent)

        self.FileName = ImageFile
        image = self.Resize(wx.Image(ImageFile))
        self.Image = wx.StaticBitmap(self, wx.ID_ANY, image.ConvertToBitmap(), size=(300,300))
        self.CheckBox = wx.CheckBox(self, wx.ID_ANY)
        self.ImageName = wx.TextCtrl(self, wx.ID_ANY, ImageFile)
        self.Bind(wx.EVT_TEXT, self.Check, self.ImageName)
        self.ImageDimensions = wx.StaticText(self, wx.ID_ANY, 'Image Dimensions: {0} x {1}'.format(wx.Image(ImageFile).GetWidth(), wx.Image(ImageFile).GetHeight()))

        self.HSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.VSizer = wx.StaticBoxSizer(wx.VERTICAL, self)

        self.HSizer.Add(self.CheckBox, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        self.HSizer.Add(self.ImageName, 0, wx.ALL|wx.EXPAND, 5)

        self.VSizer.Add(self.Image, 0, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.CENTER, 5)
        self.VSizer.Add(self.ImageDimensions, 0, wx.ALL|wx.CENTER, 10)
        self.VSizer.Add(self.HSizer, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(self.VSizer)
        self.Fit()

    def Check(self, event):
        self.CheckBox.SetValue(True)

    def Resize(self, image):
        scale = False
        if image.GetWidth() > 300: scale = True
        if image.GetHeight() > 300: scale = True
        if scale: image = image.Scale(300,300)
        return image

    def GetImageName(self):
        return self.FileName

    def GetCheckStatus(self):
        return self.CheckBox.GetValue()

    def SetCheckStatus(self, state):
        self.CheckBox.SetValue(state)

# Panel Class that displays 
class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.frame = parent
        self.frame.Discontinue = False

        font = wx.Font(24, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.Title = wx.StaticText(self, wx.ID_ANY, 'Image Downloader')
        self.Title.SetFont(font)

        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.Prompt = wx.StaticText(self, wx.ID_ANY, 'Enter link:')
        self.PromptInput = wx.TextCtrl(self, wx.ID_ANY, '')
        self.PromptEnter = wx.Button(self, wx.ID_ANY, 'Enter')
        self.Bind(wx.EVT_BUTTON, self.ImageDownload, self.PromptEnter)
        self.Prompt.SetFont(font)
        self.PromptInput.SetFont(font)
        self.PromptEnter.SetFont(font)

        self.SaveFolder = wx.StaticText(self, wx.ID_ANY, 'Save Folder: ')
        self.SaveFolderInput = wx.TextCtrl(self, wx.ID_ANY, os.getcwd(), style=wx.TE_READONLY)
        self.SaveFolderSelect = wx.Button(self, wx.ID_ANY, 'Browse')
        self.Bind(wx.EVT_BUTTON, self.PickFolder, self.SaveFolderSelect)
        self.SaveFolder.SetFont(font)
        self.SaveFolderInput.SetFont(font)
        self.SaveFolderSelect.SetFont(font)

        self.ErrorDisplay = wx.StaticText(self, wx.ID_ANY, '')
        self.ErrorDisplay.SetFont(font)

        self.MainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SubSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self)
        self.PromptSizer = wx.BoxSizer(wx.VERTICAL)
        self.InputSizer = wx.BoxSizer(wx.VERTICAL)
        self.ButtonSizer = wx.BoxSizer(wx.VERTICAL)

        self.PromptSizer.Add(self.Prompt, 1, wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, 5)
        self.PromptSizer.Add(self.SaveFolder, 1, wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, 5)

        self.InputSizer.Add(self.PromptInput, 1, wx.ALL|wx.EXPAND, 5)
        self.InputSizer.Add(self.SaveFolderInput, 1, wx.ALL|wx.EXPAND, 5)

        self.ButtonSizer.Add(self.PromptEnter, 1, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5)
        self.ButtonSizer.Add(self.SaveFolderSelect, 1, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5)

        self.SubSizer.Add(self.PromptSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SubSizer.Add(self.InputSizer, 1, wx.ALL|wx.EXPAND, 5)
        self.SubSizer.Add(self.ButtonSizer, 0, wx.ALL|wx.EXPAND, 5)

        self.MainSizer.Add(self.Title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.MainSizer.Add(self.SubSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.MainSizer.Add(self.ErrorDisplay, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        self.SetSizer(self.MainSizer)
        self.Fit()

    def PickFolder(self, event):
        with wx.DirDialog(None, "Choose Save Folder", "", wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST|wx.DD_CHANGE_DIR) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL|wx.ID_OK: return
        self.SaveFolderInput.SetValue(os.getcwd())

    def SetError(self, ErrorMessage, Status):
        if Status: self.ErrorDisplay.SetForegroundColour(wx.Colour(0,0,255))
        else: self.ErrorDisplay.SetForegroundColour(wx.Colour(255,0,0))

        self.MainSizer.Hide(self.ErrorDisplay)
        self.ErrorDisplay.SetLabel(ErrorMessage)
        self.MainSizer.Show(self.ErrorDisplay)
        self.MainSizer.Layout()

    def ImageDownload(self, event):
        self.frame.Discontinue, self.frame.CloseLock = True, True
        self.frame.DisableButtons()
        
        if self.frame.VPanelSizer.IsShown(self.frame.ImagePanel):
            self.frame.ImageButtons.Cancel()

        Link = self.PromptInput.GetValue()
        self.Status, self.ErrorMessage = imagescraper.error_check(Link, self.SaveFolderInput.GetValue())

        if len(self.ErrorMessage) > 0: self.SetError('Error: '+self.ErrorMessage, False)
        else: self.SetError(self.ErrorMessage, True)

        if self.Status:
            ImageLinks = imagescraper.download_image(Link)
            ImageFiles = self.frame.DownloadImages(ImageLinks)
        
            if len(ImageFiles) > 0:
                self.frame.Discontinue = True
                self.frame.ImagePanel.RemoveCombos()
                self.frame.ImagePanel.AddCombos(ImageFiles)
                self.frame.ShowPanels()

            else: self.SetError('No Images were Found', False)
                
        self.frame.VPanelSizer.Layout()
        self.frame.VPanelSizer.Fit(self.frame)
        self.frame.CloseLock = False
        self.frame.EnableButtons()
        
class mainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Image Downloader')

        self.Bind(wx.EVT_CLOSE, self.Close, self)
        self.CloseLock = False
        
        self.mainPanel = MainPanel(self)
        self.ImagePanel = ImageScrollPanel(self, [])
        self.ImageButtons = ImageControls(self)

        self.VPanelSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.VPanelSizer.Add(self.mainPanel, 1, wx.ALL|wx.EXPAND)
        self.VPanelSizer.Add(self.ImagePanel, 0, wx.ALL|wx.EXPAND)
        self.VPanelSizer.Add(self.ImageButtons, 0, wx.ALL|wx.EXPAND)
        
        self.RemovePanels()
        
        self.SetSizer(self.VPanelSizer)
        self.VPanelSizer.Fit(self)
        self.SetSizeHints(self.GetSize())
        self.Center()
        self.Show()

    def DisableButtons(self):
        self.mainPanel.PromptEnter.Disable()
        self.mainPanel.SaveFolderSelect.Disable()
        self.ImageButtons.ImageSelectAll.Disable()
        self.ImageButtons.ImageDeselectAll.Disable()
        self.ImageButtons.ConfirmSelected.Disable()
        self.ImageButtons.CancelAll.Disable()

    def EnableButtons(self):
        self.mainPanel.PromptEnter.Enable()
        self.mainPanel.SaveFolderSelect.Enable()
        self.ImageButtons.ImageSelectAll.Enable()
        self.ImageButtons.ImageDeselectAll.Enable()
        self.ImageButtons.ConfirmSelected.Enable()
        self.ImageButtons.CancelAll.Enable()

    def DownloadImages(self, ImageLinks):
        LoadingFrame = wx.Frame(None, wx.ID_ANY, 'Image Downloader')
        LoadingPanel = StatusGauge(LoadingFrame, 100, 'Extracting Images ...')
        LoadingFrame.Center()
        LoadingFrame.Fit()
        LoadingFrame.Show()

        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent,}

        count = 0
        ImageFileNames = []
        Default = imagescraper.default_name()
        for Link in ImageLinks:
            ImageFile = Default+'_'+str(count)+Link[1]
            try:
                req = urllib.request.Request(Link[0], None, headers)
                Data = urllib.request.urlopen(req).read()
                File = os.open(ImageFile, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_BINARY)
                os.write(File, Data)
                os.close(File)
                ImageFileNames.append(ImageFile)
                count+=1
            except urllib.error.HTTPError as e:
                pass
            except urllib.error.URLError:
                pass
            except ValueError:
                pass
            LoadingPanel.ChangeGauge((count/len(ImageLinks))*100)
            LoadingPanel.ChangeText(str(int(LoadingPanel.Gauge.GetValue()))+' %')
            wx.Yield()

        LoadingFrame.Destroy()
        return ImageFileNames

    def RemovePanels(self):
        self.VPanelSizer.Hide(self.ImagePanel)
        self.VPanelSizer.Hide(self.ImageButtons)
        self.VPanelSizer.Layout()
        self.Fit()

    def ShowPanels(self):
        self.VPanelSizer.Show(self.ImagePanel)
        self.VPanelSizer.Show(self.ImageButtons)
        self.VPanelSizer.Layout()
        self.Fit()

    def Close(self, event):
        self.DisableButtons()
        if self.CloseLock: return
        if self.Discontinue:
            LoadingFrame = wx.Frame(None, wx.ID_ANY, 'Image Downloader')
            LoadingPanel = StatusGauge(LoadingFrame, 100, 'Removing Images ...')
            LoadingFrame.Center()
            LoadingFrame.Fit()
            LoadingFrame.Show()
            count = 0
        
            for box in self.ImagePanel.Images:
                imagescraper.remove_file(box.GetImageName())
                count+=1
                LoadingPanel.ChangeGauge((count/len(self.ImagePanel.Images))*100)
                LoadingPanel.ChangeText(str(int(LoadingPanel.Gauge.GetValue()))+' %')
                wx.Yield()
            
            LoadingFrame.Destroy()
        self.Destroy()
        


if __name__ == '__main__':
    app = wx.App()
    frame = mainFrame()
    app.MainLoop()
