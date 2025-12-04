const API_URL = "http://127.0.0.1:5000/pets";

async function loadPets() {
  const res = await fetch(API_URL);
  const pets = await res.json();
  const div = document.getElementById("pets");
  
  div.innerHTML = pets.map(p => `
    <div class="pet-card">
      <b>${p.nome}</b> (${p.raca})<br>
      ${p.foto ? `<img src="http://127.0.0.1:5000/uploads/${p.foto}" width="100">` : ""}
      <button onclick="window.location.href='pet_view.html?id=${p.id}'">Ver</button>
      <button onclick="window.location.href='edit_pet.html?id=${p.id}'">Editar</button>
      <button onclick="deletePet(${p.id})">Deletar</button>
    </div>
  `).join("");
}

async function addPet(e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);

  await fetch("http://127.0.0.1:5000/pets", {
    method: "POST",
    body: formData
  });

  alert("Pet adicionado!");
  window.location.href = "pet_list.html";
}


async function deletePet(id) {
  if (confirm("Deseja deletar este pet?")) {
    await fetch(`${API_URL}/${id}`, { method: "DELETE" });
    loadPets();
  }
}
