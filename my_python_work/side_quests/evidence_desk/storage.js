(function () {
  'use strict';
  const opened = new Promise((resolve, reject) => {
    const request = indexedDB.open('evidence-desk-v1', 1);
    request.onupgradeneeded = () => {
      request.result.createObjectStore('projects', {keyPath: 'id'});
      const images = request.result.createObjectStore('images', {keyPath: 'id'});
      images.createIndex('projectId', 'projectId');
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(new Error('Browser storage is unavailable. Allow site storage and reopen the app.'));
  });
  async function transaction(names, mode, run) {
    const database = await opened;
    return new Promise((resolve, reject) => {
      const tx = database.transaction(names, mode);
      let result;
      tx.oncomplete = () => resolve(result);
      tx.onerror = () => reject(tx.error || new Error('Could not save. Browser storage may be full.'));
      tx.onabort = () => reject(tx.error || new Error('The save was interrupted.'));
      const done = value => { result = value; };
      try { run(tx, done); } catch (error) { tx.abort(); reject(error); }
    });
  }
  const getProjects = () => transaction(['projects'], 'readonly', (tx, done) => {
    const request = tx.objectStore('projects').getAll();
    request.onsuccess = () => done(request.result.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)));
  });
  const getImages = projectId => transaction(['images'], 'readonly', (tx, done) => {
    const request = tx.objectStore('images').index('projectId').getAll(projectId);
    request.onsuccess = () => done(request.result.sort((a, b) => a.createdAt.localeCompare(b.createdAt)));
  });
  const save = project => transaction(['projects'], 'readwrite', tx => tx.objectStore('projects').put(project));
  const putImage = image => transaction(['images'], 'readwrite', tx => tx.objectStore('images').put(image));
  const removeImage = id => transaction(['images'], 'readwrite', tx => tx.objectStore('images').delete(id));
  async function removeProject(id) {
    const images = await getImages(id);
    return transaction(['projects', 'images'], 'readwrite', tx => {
      tx.objectStore('projects').delete(id);
      for (const image of images) tx.objectStore('images').delete(image.id);
    });
  }
  const restore = (project, images) => transaction(['projects', 'images'], 'readwrite', tx => {
    tx.objectStore('projects').put(project);
    for (const image of images) tx.objectStore('images').put(image);
  });
  window.EvidenceStore = {getProjects, getImages, save, putImage, removeImage, removeProject, restore};
})();
