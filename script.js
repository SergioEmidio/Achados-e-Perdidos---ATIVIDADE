const mural = document.getElementById("mural");
const vazio = document.getElementById("vazio");
const contagem = document.getElementById("contagem");
const dialogo = document.getElementById("dialogo");
const form = document.getElementById("form");
const erroForm = document.getElementById("erro-form");
const toast = document.getElementById("toast");

let tipoAtual = "todos";
let buscaAtual = "";
let timerToast, timerBusca;

// ---------- Feedback ----------
function avisar(mensagem, erro = false) {
  toast.textContent = mensagem;
  toast.classList.toggle("erro-toast", erro);
  toast.classList.add("visivel");
  clearTimeout(timerToast);
  timerToast = setTimeout(() => toast.classList.remove("visivel"), 3000);
}

// ---------- Renderização ----------
function el(tag, classe, texto) {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texto !== undefined) e.textContent = texto; // textContent evita XSS
  return e;
}

function linha(rotulo, valor) {
  const p = el("p", "dados");
  p.append(el("strong", "", rotulo + " "), document.createTextNode(valor));
  return p;
}

function criarEtiqueta(item) {
  const card = el("article", `etiqueta ${item.tipo}${item.resolvido ? " resolvido" : ""}`);

  const rotulo = item.resolvido ? "Resolvido" : item.tipo === "perdido" ? "Perdido" : "Encontrado";
  card.append(el("span", "selo", rotulo), el("h2", "", item.nome));

  if (item.imagem_url) {
    const img = el("img");
    img.src = item.imagem_url;
    img.alt = `Foto de ${item.nome}`;
    card.append(img);
  }

  card.append(
    el("p", "", item.descricao),
    linha("Local:", item.local),
    linha("Contato:", item.contato),
    el("p", "data", `Cadastrado em ${item.criado_em}`)
  );

  const botao = el("button", "btn", item.resolvido ? "Reabrir item" : "Marcar como resolvido");
  botao.type = "button";
  botao.addEventListener("click", () => alternarResolvido(item));
  card.append(botao);
  return card;
}

async function carregar() {
  const params = new URLSearchParams({ tipo: tipoAtual, q: buscaAtual });
  try {
    const resp = await fetch(`/api/itens?${params}`);
    const itens = await resp.json();
    mural.replaceChildren(...itens.map(criarEtiqueta));
    vazio.hidden = itens.length > 0;
    contagem.textContent = itens.length ? `${itens.length} item(ns)` : "";
  } catch {
    avisar("Não foi possível carregar os itens.", true);
  }
}

// ---------- Ações ----------
async function alternarResolvido(item) {
  try {
    const resp = await fetch(`/api/itens/${item.id}/resolver`, { method: "PATCH" });
    if (!resp.ok) throw new Error();
    const atualizado = await resp.json();
    avisar(atualizado.resolvido ? "Item marcado como resolvido." : "Item reaberto.");
    carregar();
  } catch {
    avisar("Não foi possível atualizar o item.", true);
  }
}

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  erroForm.hidden = true;
  try {
    const resp = await fetch("/api/itens", { method: "POST", body: new FormData(form) });
    const dados = await resp.json();
    if (!resp.ok) {
      erroForm.textContent = dados.erro || "Não foi possível salvar.";
      erroForm.hidden = false;
      return;
    }
    dialogo.close();
    form.reset();
    avisar("Item cadastrado.");
    carregar();
  } catch {
    erroForm.textContent = "Erro de conexão. Tente novamente.";
    erroForm.hidden = false;
  }
});

document.getElementById("abrir-form").addEventListener("click", () => {
  erroForm.hidden = true;
  dialogo.showModal();
});
document.getElementById("cancelar").addEventListener("click", () => dialogo.close());

document.querySelectorAll(".filtro").forEach((btn) =>
  btn.addEventListener("click", () => {
    document.querySelector(".filtro.ativo").classList.remove("ativo");
    btn.classList.add("ativo");
    tipoAtual = btn.dataset.tipo;
    carregar();
  })
);

document.getElementById("busca").addEventListener("input", (ev) => {
  clearTimeout(timerBusca);
  timerBusca = setTimeout(() => {
    buscaAtual = ev.target.value.trim();
    carregar();
  }, 250);
});

carregar();