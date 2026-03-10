#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Automação - Monitor de Vagas InHire
==============================================

Este script executa o notebook Jupyter via linha de comando.
Útil para agendamento (Cron, Task Scheduler, GitHub Actions).

Uso:
    python executar_monitor.py
    
    # Com argumentos opcionais:
    python executar_monitor.py --empresas "kpmg,alura,ifood" --telegram

Autor: Sistema Automatizado
Data: Março 2026
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime
import json


def executar_notebook(notebook_path, params=None):
    """
    Executa Jupyter Notebook via nbconvert.
    
    Args:
        notebook_path (str): Caminho para o arquivo .ipynb
        params (dict): Parâmetros opcionais para injetar no notebook
    
    Returns:
        bool: True se execução bem-sucedida
    """
    print("=" * 70)
    print("🚀 INICIANDO EXECUÇÃO DO MONITOR DE VAGAS")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"📓 Notebook: {notebook_path}")
    print("-" * 70)
    
    # Verifica se notebook existe
    if not os.path.exists(notebook_path):
        print(f"❌ ERRO: Notebook não encontrado em {notebook_path}")
        return False
    
    # Comando para executar notebook
    cmd = [
        'jupyter', 'nbconvert',
        '--to', 'notebook',
        '--execute',
        '--inplace',  # Atualiza o notebook original com outputs
        notebook_path
    ]
    
    # Alternativa: salvar em novo arquivo
    # '--output', f'executed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.ipynb'
    
    try:
        print("🔄 Executando notebook...\n")
        
        # Executa comando
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # Timeout de 10 minutos
        )
        
        if result.returncode == 0:
            print("\n✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
            print("-" * 70)
            
            # Mostra últimas linhas do output
            if result.stdout:
                print("\n📄 Output:")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            
            return True
        else:
            print("\n❌ ERRO NA EXECUÇÃO!")
            print("-" * 70)
            print(f"Código de retorno: {result.returncode}")
            
            if result.stderr:
                print(f"\n📄 Erro:\n{result.stderr}")
            
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏱️  TIMEOUT: Execução ultrapassou 10 minutos")
        return False
        
    except FileNotFoundError:
        print("\n❌ ERRO: Jupyter não encontrado!")
        print("   Instale com: pip install jupyter nbconvert")
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        return False


def configurar_parametros(args):
    """
    Configura parâmetros personalizados para o notebook.
    
    Args:
        args: Argumentos da linha de comando
    
    Returns:
        dict: Dicionário de parâmetros
    """
    params = {}
    
    if args.empresas:
        # Converte string separada por vírgula em lista
        params['EMPRESAS_ALVO'] = [e.strip() for e in args.empresas.split(',')]
        print(f"📊 Empresas customizadas: {params['EMPRESAS_ALVO']}")
    
    if args.delay:
        params['DELAY_REQUISICOES'] = args.delay
        print(f"⏱️  Delay entre requisições: {args.delay}s")
    
    if args.telegram:
        params['ENVIAR_TELEGRAM'] = True
        print("📱 Alertas Telegram: ATIVADOS")
    
    return params


def verificar_dependencias():
    """
    Verifica se todas as dependências estão instaladas.
    
    Returns:
        bool: True se tudo OK
    """
    print("\n🔍 Verificando dependências...\n")
    
    dependencias = [
        'jupyter',
        'requests',
        'bs4',
        'pandas',
        'lxml',
        'tqdm',
        'fake_useragent'
    ]
    
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - NÃO INSTALADO")
            faltando.append(dep)
    
    if faltando:
        print(f"\n⚠️  Dependências faltando: {', '.join(faltando)}")
        print("\n   Instale com:")
        print(f"   pip install {' '.join(faltando)}")
        return False
    
    print("\n✅ Todas as dependências OK!\n")
    return True


def main():
    """Função principal."""
    
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='Executa monitor de vagas InHire automaticamente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  
  # Execução básica
  python executar_monitor.py
  
  # Com empresas específicas
  python executar_monitor.py --empresas "kpmg,alura,ifood"
  
  # Com Telegram e delay customizado
  python executar_monitor.py --telegram --delay 5
  
  # Verificar apenas dependências
  python executar_monitor.py --check
        """
    )
    
    parser.add_argument(
        '--empresas',
        type=str,
        help='Lista de empresas separadas por vírgula (ex: "kpmg,alura,ifood")'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=2,
        help='Delay entre requisições em segundos (padrão: 2)'
    )
    
    parser.add_argument(
        '--telegram',
        action='store_true',
        help='Ativar envio de alertas via Telegram'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Apenas verificar dependências sem executar'
    )
    
    parser.add_argument(
        '--notebook',
        type=str,
        default='monitor_vagas_inhire.ipynb',
        help='Caminho para o notebook (padrão: monitor_vagas_inhire.ipynb)'
    )
    
    args = parser.parse_args()
    
    # Verificar dependências
    deps_ok = verificar_dependencias()
    
    if args.check:
        # Modo verificação apenas
        sys.exit(0 if deps_ok else 1)
    
    if not deps_ok:
        print("\n❌ Corrija as dependências antes de executar.")
        sys.exit(1)
    
    # Configurar parâmetros
    params = configurar_parametros(args)
    
    # Executar notebook
    print("\n" + "=" * 70)
    sucesso = executar_notebook(args.notebook, params)
    print("=" * 70)
    
    if sucesso:
        print("\n🎉 Monitor executado com sucesso!")
        print(f"📁 Verifique os arquivos CSV/Excel gerados")
        sys.exit(0)
    else:
        print("\n❌ Falha na execução do monitor")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução cancelada pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
