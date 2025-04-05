function changeState(clickedCheckbox) {
  if(clickedCheckbox.id === "flexCheckDefault") {
    clickedCheckbox.setAttribute('id', "flexCheckChecked");
    clickedCheckbox.checked = true;
  } else {
    clickedCheckbox.setAttribute('id', "flexCheckDefault");
    clickedCheckbox.checked = false;
  }
}

function changeStateSwitch(clickedCheckbox) {
  if(clickedCheckbox.id === "flexSwitchCheckDefault") {
    clickedCheckbox.setAttribute('id', "flexSwitchCheckChecked");
    clickedCheckbox.checked = true;
  } else {
    clickedCheckbox.setAttribute('id', "flexSwitchCheckDefault");
    clickedCheckbox.checked = false;
  }
}

function groupAdd() {
  const inputGroupName = document.getElementById('gp-name').value;
  const ModalNewGroup = document.getElementById('new-gp');
  const ModalNewGroupClose = bootstrap.Modal.getInstance(ModalNewGroup);

  fetch('/api/group/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: inputGroupName
      })
    })
    .then(response => {
      if(inputGroupName === '') {
        alert('Empty data.');
        return;
      }
      if(!response.ok) throw new Error(response.status)
      return response.json();
    })
    .then(data => {
      if(data.status !== true) {
        alert('Duplicate name.');
      } else {
        ModalNewGroupClose.hide();
        location.reload();
    }
    })
    .catch(err => console.log('Error status code: ' + err.message));
}

function playlistAdd() {
  const inputPlaylistName = document.getElementById('gp-name').value;
  const ModalNewPlaylist = document.getElementById('new-gp');
  const ModalNewPlaylistClose = bootstrap.Modal.getInstance(ModalNewPlaylist);

  fetch('/api/playlist/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: inputPlaylistName
      })
    })
    .then(response => {
      if(inputPlaylistName === '') {
        alert('Empty data.');
        return;
      }
      if(!response.ok) throw new Error(response.status)
      return response.json();
    })
    .then(data => {
      if(data.status !== true) {
        alert('Duplicate name.');
      } else {
        ModalNewPlaylistClose.hide();
        location.reload();
    }
    })
    .catch(err => console.log('Error status code: ' + err.message));
}

function userAccess() {
  const checkboxesGroup = document.querySelectorAll('input[class="form-check-input group"]');
  const checkboxesPlaylist = document.querySelectorAll('input[class="form-check-input playlist"]');
  const userID = document.querySelector(".user-info").id;
  const ModalModifyUser = document.getElementById('access-user');
  const ModalModifyUserClose = bootstrap.Modal.getInstance(ModalModifyUser);
  const checked = [];
  const unchecked = [];
  checkboxesGroup.forEach(function(checkbox) {
    if(checkbox.id === "flexCheckChecked") {
      checked.push(checkbox.value);
    } else {
      unchecked.push(checkbox.value);
    }
  });
  checkboxesPlaylist.forEach(function(checkbox) {
    if(checkbox.id === "flexCheckChecked") {
      checked.push(checkbox.value);
    } else {
      unchecked.push(checkbox.value);
    }
  });
  fetch('/api/user/access', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user: userID,
        on: checked,
        off: unchecked
      })
    })
    .then(response => {
      if(!response.ok) throw new Error(response.status)
      return response.json();
    })
    .then(data => {
      if(data.status !== true) {
        alert(data.message);
      } else {
        ModalModifyUserClose.hide();
        setTimeout(() => {
          location.reload();
        }, 100);
    }
    })
    .catch(err => console.log('Error status code: ' + err.message));
}

function userAdd() {
  const inputUserName = document.getElementById('user-name').value;
  const inputUserEmail = document.getElementById('user-email').value;
  const checkboxPassword = document.getElementById('flexCheckChecked');
  const manualPassword = document.getElementById('password').value;
  const ModalNewUser = document.getElementById('new-user');
  const ModalNewUserClose = bootstrap.Modal.getInstance(ModalNewUser);
  let customBody = {}
  checkboxPassword ?  customBody = {name: inputUserName, email: inputUserEmail, pwd: manualPassword}:customBody = {name: inputUserName, email: inputUserEmail}

  fetch('/api/user/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(customBody)
    })
    .then(response => {
      if(inputUserName === '' || inputUserEmail === '') {
        alert('Empty data.');
        return;
      }
      if(!response.ok) throw new Error(response.status)
      return response.json();
    })
    .then(data => {
      if(data.status !== true) {
        alert(data.message);
      } else {
        ModalNewUserClose.hide();
        location.reload();
    }
    })
    .catch(err => console.log('Error status code: ' + err.message));
}

function userBlocked(bool) {
  const userID = document.querySelector(".user-info").id;
  const userName = document.getElementById('user-name').textContent;

  fetch('/api/user/state', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      userID: userID,
      userName: userName,
      state: bool
    })
  })
  .then(response => {
    if(!response.ok) throw new Error(response.status)
    return response.json();
  })
  .then(data => {
    if(data.status !== true) {
      alert(data.message)
    }
  })
  .catch(err => console.log('Error status code: ' + err.message));
}

function upload() {
  const form = document.getElementById('upload');
  const fileInput = document.getElementById('formFile').files[0];
  const ModalUpload = document.getElementById('upload');
  const uploadMessage = document.querySelector('.modal-body p');
  const ModalUploadClose = bootstrap.Modal.getInstance(ModalUpload);
  const progressBarContainer = document.getElementById('progress-bar-container');
  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-text');
  let formData = new FormData();

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const fileName = document.getElementById('filename').value;
    
    if (!fileName) {
      alert('Empty "Filename".');
      return;
    }

    uploadMessage.textContent = `Upload file: ${fileName}...`;
    progressBarContainer.style.display = 'block';
    progressBar.style.width = '0%';
    formData.append(fileName.slice(0, 255), fileInput);
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload', true);
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100;
        progressBar.style.width = percentComplete + '%';
        progressText.textContent = `${Math.round(percentComplete)}%`;
      }
    });
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        if (response.status !== true) {
          alert(response.message);
        } else {
          ModalUploadClose.hide();
          location.reload();
        }
      } else {
        alert('Error when uploading a file.');
      }
      progressBarContainer.style.display = 'none';
      form.reset();
    });
    xhr.addEventListener('error', () => {
      alert('Error when uploading a file.');
      progressBarContainer.style.display = 'none';
      form.reset();
    });
    xhr.send(formData);
  });
}

function editVideo() {
  const checkboxName = document.querySelector('input[class="form-check-input name"]');
  const checkboxesGroup = document.querySelectorAll('input[class="form-check-input group"]');
  const checkboxesPlaylist = document.querySelectorAll('input[class="form-check-input playlist"]');
  const videoName = document.getElementById('set-name').value;
  const videoLink = document.querySelector(".video-info").id;
  const ModalEditVideo = document.getElementById('edit-video');
  const ModalEditVideoClose = bootstrap.Modal.getInstance(ModalEditVideo);
  const checked = [];
  const unchecked = [];
  checkboxesGroup.forEach(function(checkbox) {
    if(checkbox.id === "flexCheckChecked") {
      checked.push(checkbox.value);
    } else {
      unchecked.push(checkbox.value);
    }
  });
  checkboxesPlaylist.forEach(function(checkbox) {
    if(checkbox.id === "flexCheckChecked") {
      checked.push(checkbox.value);
    } else {
      unchecked.push(checkbox.value);
    }
  });
  let customBody = {}
  checkboxName.getAttribute("id")==="flexCheckChecked" 
    ? customBody = {link: videoLink, videoName: videoName, on: checked, off: unchecked}
    : customBody = {link: videoLink, on: checked, off: unchecked}
  fetch('/api/video/edit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(customBody)
  })
  .then(response => {
    if(!response.ok) throw new Error(response.status)
    return response.json();
  })
  .then(data => {
    if(data.status !== true) {
      alert(data.message);
      
    } else {
      ModalEditVideoClose.hide();
      setTimeout(() => {
        location.reload();
      }, 100);
  }
  })
  .catch(err => console.log('Error status code: ' + err.message));
}

function shareVideo(bool) {
  const videoLink = document.querySelector(".video-info").id;
  const videoName = document.getElementById('video-name').textContent;

  fetch('/api/video/share', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      videoLink: videoLink,
      videoName: videoName,
      state: bool
    })
  })
  .then(response => {
    if(!response.ok) throw new Error(response.status)
    return response.json();
  })
  .then(data => {
    console.log(data);
    if(data.status !== true) {
      alert(data.message)
    } else {
      location.reload();
    }
  })
  .catch(err => console.log('Error status code: ' + err.message));
}

function setPassword() {
  const userID = document.querySelector(".user-info").id;
  const userName = document.getElementById('user-name').textContent;
  const manualPassword = document.getElementById('password').value;
  const ModalModifyUser = document.getElementById('edit-user');
  const ModalModifyUserClose = bootstrap.Modal.getInstance(ModalModifyUser);

  fetch('/api/user/set-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      userID: userID,
      userName: userName,
      userPwd: manualPassword
    })
    })
    .then(response => {
      // if(manualPassword === '') {
      //   alert('Empty data.');
      //   return;
      // }
      if(!response.ok) throw new Error(response.status)
      return response.json();
    })
    .then(data => {
      if(data.status !== true) {
        alert(data.message);
      }
      // } else {
      //   ModalModifyUserClose.hide();
      //   location.reload();
      // }
    })
    .catch(err => console.log('Error status code: ' + err.message));
}

function resetPassword() {
  const userID = document.querySelector('.user-info').id;
  const userEmail = document.getElementById('user-email').textContent;
  const userName = document.getElementById('user-name').textContent;
  const ModalModifyUser = document.getElementById('edit-user');
  const ModalModifyUserClose = bootstrap.Modal.getInstance(ModalModifyUser);
  
  fetch('/api/user/reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      userID: userID,
      userEmail: userEmail,
      userName: userName,
      state: 'reset-password'
    })
    })
    .then(response => {
      if(!response.ok) throw new Error(response.status)
      return response.json();
    })
    .then(data => {
      if(data.status !== true) {
        alert(data.message);
      }
      // } else {
      //   ModalModifyUserClose.hide();
      //   location.reload();
      // }
    })
    .catch(err => console.log('Error status code: ' + err.message));
}

function admin(bool) {
  const userID = document.querySelector('.user-info').id;
  const userName = document.getElementById('user-name').textContent;
  const ModalModifyUser = document.getElementById('edit-user');
  const ModalModifyUserClose = bootstrap.Modal.getInstance(ModalModifyUser);
  fetch('/api/user/admin', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      userID: userID,
      userName: userName,
      state: bool,
    })
    })
    .then(response => {
      if(!response.ok) throw new Error(response.status)
      return response.json();
    })
    .then(data => {
      if(data.status !== true) {
        alert(data.message);
      }
      // } else {
      //   ModalModifyUserClose.hide();
      //   location.reload();
      // }
    })
    .catch(err => console.log('Error status code: ' + err.message));
}
