#         Date: 10 Aug 2016
#       Author: Angelo PACE
# Organisation: GeoScience Australia
#  Description: Dump members of the AD 'Water' group
#               i.e. U number, Persons Full Name

# Edit groupname to suit
#$GroupName = "Water"
#$UserList = @()

#$GWaterGroup = Net Group $GroupName /Domain


   $tmpUsers = "u25834"
#   ForEach ($tmpUser In $tmpUsers) {
      If ($tmpUser.Length -EQ 5) {
         $User = New-Object System.Object
         $User | Add-Member -type NoteProperty -name uNumber  -value "u$tmpUser"
         $User | Add-Member -type NoteProperty -name FullName -value (@(Net User "u$tmpUser" /Domain)[3]).Substring(29)
         $UserList += $User
         }
#      }

$UserList | Sort-Object FullName | Export-CSV "$($Env:UserProfile)\Desktop\test.csv" -Delimiter "," -NoTypeInformation
