BOOST_LIB=boost_python-py27
PYTHON_LIB=python2.7
PYTHON_INC=/usr/include/python2.7
PYTHON_LIB_PATH=/usr/lib/python2.7/config-x86_64-linux-gnu/

CXX=g++
CXXFLAGS=-Wall -pedantic -fPIC -std=c++14

CLIENT_DEPS=src/Client.cpp src/Client.hpp src/PyXchangeFwd.hpp
TRADER_DEPS=src/Trader.cpp src/Trader.hpp src/PyXchangeFwd.hpp
ORDER_DEPS=src/Order.cpp src/Order.hpp src/PyXchangeFwd.hpp
ORDERBOOK_DEPS=src/orderbook/OrderBook.cpp src/orderbook/OrderBook.hpp src/Order.hpp src/orderbook/OrderContainer.hpp src/Message.hpp src/PyXchangeFwd.hpp
CREATEORDER_DEPS=src/orderbook/CreateOrder.cpp src/orderbook/OrderBook.hpp src/Order.hpp src/orderbook/OrderContainer.hpp src/Message.hpp src/PyXchangeFwd.hpp
MATCHER_DEPS=src/Matcher.cpp src/Matcher.hpp src/Client.hpp src/Trader.hpp src/orderbook/OrderBook.hpp src/Message.hpp src/Utils.hpp src/PyXchangeFwd.hpp
PYXCHANGEO_DEPS=src/PyXchange.cpp src/PyXchangeFwd.hpp src/Client.hpp src/Trader.hpp src/Matcher.hpp src/Utils.hpp
PYXCHANGE_DEPS=build/Client.o build/Trader.o build/Order.o build/OrderBook.o build/CreateOrder.o build/Matcher.o build/PyXchange.o

all: pyxchange.so

test: all
	./smoketest.py -v

run: all
	./pyxchange_server.py

clean:
	rm -vf build/*.o pyxchange.so

build/Client.o: $(CLIENT_DEPS)
	$(CXX) $(CXXFLAGS) -o build/Client.o      -c src/Client.cpp    -I$(PYTHON_INC)

build/Trader.o: $(TRADER_DEPS)
	$(CXX) $(CXXFLAGS) -o build/Trader.o      -c src/Trader.cpp    -I$(PYTHON_INC)

build/Order.o: $(ORDER_DEPS)
	$(CXX) $(CXXFLAGS) -o build/Order.o       -c src/Order.cpp     -I$(PYTHON_INC)

build/OrderBook.o: $(ORDERBOOK_DEPS)
	$(CXX) $(CXXFLAGS) -o build/OrderBook.o   -c src/orderbook/OrderBook.cpp -I$(PYTHON_INC)

build/CreateOrder.o: $(CREATEORDER_DEPS)
	$(CXX) $(CXXFLAGS) -o build/CreateOrder.o -c src/orderbook/CreateOrder.cpp -I$(PYTHON_INC)

build/Matcher.o: $(MATCHER_DEPS)
	$(CXX) $(CXXFLAGS) -o build/Matcher.o     -c src/Matcher.cpp   -I$(PYTHON_INC)

build/PyXchange.o: $(PYXCHANGEO_DEPS)
	$(CXX) $(CXXFLAGS) -o build/PyXchange.o   -c src/PyXchange.cpp -I$(PYTHON_INC)

pyxchange.so: $(PYXCHANGE_DEPS)
	$(CXX) $(CXXFLAGS) -o pyxchange.so -l$(BOOST_LIB) -l$(PYTHON_LIB) -shared -rdynamic $(PYXCHANGE_DEPS) -L$(PYTHON_LIB_PATH)

	