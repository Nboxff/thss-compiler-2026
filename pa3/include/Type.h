#pragma once

#include <cstdint>
#include <vector>

// Abstract base class for every type.  A type is identified by its TypeID.
class Type {
public:
  enum TypeID {
    VoidTypeID,
    IntTypeID,
    ArrayTypeID,
    FunctionTypeID,
  };

  virtual ~Type() = default;

  TypeID getTypeID() const { return id_; }
  bool isFunctionType() const { return id_ == FunctionTypeID; }

protected:
  explicit Type(TypeID id) : id_(id) {}

private:
  TypeID id_;
};

// TODO: You may add derived classes for specific types (e.g., IntType,
// ArrayType, FunctionType) if needed.
