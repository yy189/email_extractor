Excel record macro to extract hyperlinks:

Sub ExtractHL()

    For Each cell In Range("B2:B1557")
        If cell.Hyperlinks.Count > 0 Then
            cell.Offset(0, 1) = cell.Hyperlinks(1).Address
        End If
    Next
    
End Sub
