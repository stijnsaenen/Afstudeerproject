# ODCC options
# See https://www.cleito.com/products/odcc/documentation for more details

# odcc.remove.domain.in.username
# e.g. $false
$odccRemoveDomainInUserName=$true

# odcc.fetch.users.from.groups
# e.g. @("Paris_Users","London_Users")
$odccFetchUsersFromGroups=@()

# odcc.limit.groups
# e.g. @("jira-software-users","confluence-users")
$odccLimitGroups=@()

# Functions

Function get-users-from-groups($groupNameList=@()){
    $userList=@()
    if ($groupNameList.count -gt 0){
        foreach($groupName in $groupNameList){
            $group=Get-AzureADGroup -Filter "displayName eq '$groupName'"
            $groupMembers=Get-AzureADGroupMember -ObjectId $group.objectId | Where-Object {$_.objectType -eq 'User'}
            foreach($user in $groupMembers){
                if ($userList -notcontains $user){
                    $userList += $user
                }
            }
        }
    }else{
        $userList=Get-AzureADUser -All $true
    } 
    return $userList
}

Function fetch-users
{
    $UserResults=@()
    $userList=get-users-from-groups($odccFetchUsersFromGroups)
    
    foreach($user in $userList){
        $userName=$user.userPrincipalName
        if ($odccRemoveDomainInUserName){
            $userName=$userName.Split("@")[0]
        }
        $UserProperties = @{
        UserName=$userName
        FirstName=$user.givenName
        LastName=$user.surname
        EmailAddress=$user.mail
        Password=random-password
        UserId=$user.objectID
        }
        $UserResults += New-Object psobject -Property $UserProperties
    }
    return $UserResults
}

Function fetch-group-memberships
{
    $GroupMembershipResults=@()
    $userList=get-users-from-groups($odccFetchUsersFromGroups)
    
    foreach($user in $userList){
        $userGroups=Get-AzureADUserMembership -All $true -ObjectId $user.objectId
        foreach($userGroup in $userGroups){
            $userName=$user.userPrincipalName
            if ($odccRemoveDomainInUserName){
                $userName=$userName.Split("@")[0]
            }
            if (($odccLimitGroups.count -eq 0) -or (($odccLimitGroups.count -gt 0) -and ($odccLimitGroups -contains $userGroup.displayName))){
                $UserGroupMembershipProperties = @{
                    UserName=$userName
                    GroupName=$userGroup.displayName
                    UserId=$user.objectID
                }
                $GroupMembershipResults += New-Object psobject -Property $UserGroupMembershipProperties
            }
        }
    }
    return $GroupMembershipResults
}

# Thanks to https://blogs.technet.microsoft.com/herbchung/2015/04/14/how-to-exportimport-the-identity-from-azure-ad-to-local-ad/
Function random-password ($length = 8)
{
    $punc = 46..46
    $digits = 48..57
    $letters = 65..90 + 97..122

    $password = get-random -count $length `
        -input ($punc + $digits + $letters) |
            % -begin { $aa = $null } `
            -process {$aa += [char]$_} `
            -end {$aa}

    return $password
}

# Main

Connect-AzureAD

fetch-users | Select-Object UserName, FirstName, LastName, EmailAddress, Password, UserId | Export-Csv -Encoding UTF8 -NoTypeInformation -Path 'users_file.csv'
fetch-group-memberships | Select-Object UserName, GroupName, UserId | Export-Csv -Encoding UTF8 -NoTypeInformation -Path 'group_memberships_file.csv'

